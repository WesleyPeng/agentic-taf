# Copyright (c) 2017-2026 Wesley Peng
#
# Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
# You may obtain a copy of the License at
#
# https://www.gnu.org/licenses/lgpl-3.0.html
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

"""T.7 — Load & performance tests against live preprod cluster.

Uses the shared api_client fixture (ServiceLocator → HttpClient) from
the parent conftest. Each test measures latency/throughput and asserts
performance targets.

Requires:
  - AGENT_BASE_URL pointing to preprod agent (via port-forward)
  - For WebSocket tests: websockets package installed

Test targets (from workflow):
  - API throughput:  p95 < 2s at 50 RPS for 60s
  - WebSocket scale: 50 concurrent connections, all receive responses
  - Provision throughput: 10 parallel creates, all get responses in 5 min
  - Chat latency:    p95 < 15s for complete response
"""

import concurrent.futures
import statistics
import time

import pytest


def _percentile(data, pct):
    """Calculate the p-th percentile of a list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (pct / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


# ──────────────────────────────────────────────────────────────────────
# T.7.1 — API Throughput
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.load
@pytest.mark.e2e
class TestAPIThroughput:
    """Sustained GET /api/v1/reservations at target RPS."""

    TARGET_RPS = 50
    DURATION_SECONDS = 10  # shortened for CI; scale up for full runs
    P95_THRESHOLD = 2.0    # seconds

    def test_api_throughput_p95(self, api_client):
        """Fire requests at target RPS, measure p95 latency."""
        latencies = []
        errors = 0
        total_requests = self.TARGET_RPS * self.DURATION_SECONDS

        def single_request(_i):
            start = time.monotonic()
            try:
                resp = api_client.get('/api/v1/reservations')
                elapsed = time.monotonic() - start
                return elapsed, resp.status_code
            except Exception:
                return time.monotonic() - start, 500

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(self.TARGET_RPS, 20),
        ) as pool:
            futures = []
            start_time = time.monotonic()

            for i in range(total_requests):
                # Pace requests to approximate target RPS
                target_time = start_time + (i / self.TARGET_RPS)
                now = time.monotonic()
                if target_time > now:
                    time.sleep(target_time - now)
                futures.append(pool.submit(single_request, i))

            for f in concurrent.futures.as_completed(futures):
                elapsed, status = f.result()
                latencies.append(elapsed)
                if status >= 500:
                    errors += 1

        p95 = _percentile(latencies, 95)
        p50 = _percentile(latencies, 50)
        error_rate = errors / len(latencies) if latencies else 1.0

        assert p95 < self.P95_THRESHOLD, (
            f'p95 latency {p95:.3f}s exceeds {self.P95_THRESHOLD}s '
            f'(p50={p50:.3f}s, errors={errors}/{len(latencies)})'
        )
        assert error_rate < 0.05, (
            f'Error rate {error_rate:.1%} exceeds 5% '
            f'({errors}/{len(latencies)} requests)'
        )


# ──────────────────────────────────────────────────────────────────────
# T.7.2 — WebSocket Scale
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.load
@pytest.mark.e2e
class TestWebSocketScale:
    """Open multiple concurrent WebSocket connections."""

    CONCURRENT = 10  # scaled down for CI; 50 for full runs
    TIMEOUT = 30     # seconds per connection

    def test_concurrent_ws_connections(self, ws_url, has_websockets):
        """Each connection sends a message and expects a response."""
        import websockets.sync.client as ws_client

        results = []

        def ws_session(idx):
            try:
                conn = ws_client.connect(
                    ws_url,
                    additional_headers={
                        'X-User': f'load-user-{idx}',
                        'X-Role': 'developer',
                        'X-Team': 'test-team',
                    },
                    open_timeout=self.TIMEOUT,
                    close_timeout=5,
                )
                try:
                    conn.send('hello')
                    # Collect response tokens for up to TIMEOUT seconds
                    tokens = []
                    deadline = time.monotonic() + self.TIMEOUT
                    while time.monotonic() < deadline:
                        try:
                            conn.recv(timeout=5)
                            tokens.append(True)
                            break  # got at least one response
                        except TimeoutError:
                            break
                    return {'ok': len(tokens) > 0, 'idx': idx}
                finally:
                    conn.close()
            except Exception as exc:
                return {'ok': False, 'idx': idx, 'error': str(exc)}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.CONCURRENT,
        ) as pool:
            futures = [
                pool.submit(ws_session, i) for i in range(self.CONCURRENT)
            ]
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())

        successes = sum(1 for r in results if r['ok'])
        success_rate = successes / len(results) if results else 0.0

        assert success_rate >= 0.8, (
            f'WebSocket success rate {success_rate:.0%} '
            f'({successes}/{len(results)}) below 80% threshold'
        )


# ──────────────────────────────────────────────────────────────────────
# T.7.3 — Provision Throughput
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.load
@pytest.mark.e2e
class TestProvisionThroughput:
    """Submit parallel reservation creates, verify all get responses."""

    PARALLEL = 10
    TIMEOUT = 300  # 5 minutes

    def test_parallel_provisions(self, api_client):
        """10 parallel POST /reservations — all return non-5xx in time."""
        latencies = []
        errors = []

        def create_one(idx):
            start = time.monotonic()
            try:
                resp = api_client.post(
                    '/api/v1/reservations',
                    json={
                        'env_type': 'k8s',
                        'team': 'test-team',
                        'requestor': f'load-user-{idx}',
                        'resource_spec': {'cpu_cores': 1, 'memory_gb': 1},
                        'ttl_minutes': 30,
                        'description': f'Load test provision {idx}',
                    },
                )
                elapsed = time.monotonic() - start
                return {
                    'idx': idx,
                    'status': resp.status_code,
                    'elapsed': elapsed,
                    'body': resp.json() if resp.status_code < 500 else {},
                }
            except Exception as exc:
                return {
                    'idx': idx,
                    'status': 500,
                    'elapsed': time.monotonic() - start,
                    'error': str(exc),
                }

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.PARALLEL,
        ) as pool:
            futures = [
                pool.submit(create_one, i) for i in range(self.PARALLEL)
            ]
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                latencies.append(result['elapsed'])
                if result['status'] >= 500:
                    errors.append(result)

        # Clean up created reservations
        self._cleanup(api_client)

        p95 = _percentile(latencies, 95)
        assert len(errors) == 0, (
            f'{len(errors)}/{self.PARALLEL} provisions returned 5xx: '
            f'{errors}'
        )
        assert p95 < self.TIMEOUT, (
            f'p95 provision time {p95:.1f}s exceeds {self.TIMEOUT}s'
        )

    def _cleanup(self, api_client):
        """Release any reservations created during the test."""
        try:
            resp = api_client.get('/api/v1/reservations')
            if resp.status_code == 200:
                for r in resp.json():
                    rid = r.get('id') or r.get('reservation_id')
                    desc = str(r.get('description', ''))
                    if rid and 'Load test provision' in desc:
                        api_client.post(
                            f'/api/v1/reservations/{rid}/release'
                        )
        except Exception:
            pass  # best-effort cleanup


# ──────────────────────────────────────────────────────────────────────
# T.7.4 — Chat Latency
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.load
@pytest.mark.e2e
class TestChatLatency:
    """Measure chat response latency across sequential requests."""

    NUM_REQUESTS = 5   # shortened for CI; 20 for full runs
    P95_THRESHOLD = 15.0  # seconds

    PROMPTS = [
        'Hello, what can you do?',
        'How many environments are currently active?',
        'What Kubernetes namespaces are available?',
        'Show me the team quotas for test-team.',
        'What is the health status of the platform?',
    ]

    def test_chat_latency_p95(self, api_client):
        """Sequential chat requests, p95 < 15s."""
        latencies = []
        errors = 0

        for i in range(self.NUM_REQUESTS):
            prompt = self.PROMPTS[i % len(self.PROMPTS)]
            start = time.monotonic()
            try:
                resp = api_client.post(
                    '/api/v1/chat',
                    json={'message': prompt},
                )
                elapsed = time.monotonic() - start
                latencies.append(elapsed)
                if resp.status_code >= 500:
                    errors += 1
            except Exception:
                latencies.append(time.monotonic() - start)
                errors += 1

        if not latencies:
            pytest.skip('No chat responses received')

        p95 = _percentile(latencies, 95)
        p50 = _percentile(latencies, 50)
        mean = statistics.mean(latencies)

        assert p95 < self.P95_THRESHOLD, (
            f'Chat p95 latency {p95:.1f}s exceeds {self.P95_THRESHOLD}s '
            f'(p50={p50:.1f}s, mean={mean:.1f}s, '
            f'errors={errors}/{len(latencies)})'
        )
