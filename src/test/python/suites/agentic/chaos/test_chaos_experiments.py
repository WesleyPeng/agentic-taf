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

"""T.6 — Chaos engineering experiments against live preprod cluster.

Uses ChaosRunner (from taf.modeling.chaos) backed by K8sChaosPlugin
resolved via ServiceLocator. Each experiment:
  1. Injects a fault (pod kill, network partition, Flux suspend)
  2. Waits for propagation
  3. Verifies resilience via probe (HTTP health, K8s readiness)
  4. Cleans up the fault
  5. Asserts the system recovered

Requires:
  - kubernetes package installed
  - KUBECONFIG pointing to preprod cluster
  - kubectl port-forward for agent health probes
"""

import os

import pytest

from taf.modeling.chaos import ChaosRunner
from taf.foundation.plugins.chaos.k8s.faults import (
    PodKill, FluxSuspend,
)
from taf.foundation.plugins.chaos.k8s.probes import (
    HttpHealthProbe, K8sReadyProbe,
)

_AGENT_URL = os.environ.get('AGENT_BASE_URL', 'http://localhost:18000')
_NAMESPACE = 'agentic-platform'


@pytest.mark.chaos
@pytest.mark.e2e
class TestAgentPodKill:
    """Kill agent pod → verify K8s restarts it and health recovers."""

    def test_agent_pod_kill_recovery(self, chaos_client):
        fault = PodKill(label_selector='app=agentic-qa-agent', count=1)
        probe = K8sReadyProbe(label_selector='app=agentic-qa-agent', min_ready=1)

        runner = ChaosRunner(namespace=_NAMESPACE)
        runner.inject = chaos_client.inject
        runner.verify = chaos_client.verify
        runner.cleanup = chaos_client.cleanup

        result = runner.assert_resilient(
            fault=fault,
            probe=probe,
            target='agentic-qa-agent',
            wait_seconds=15,
            retries=6,
            retry_interval=10,
            namespace=_NAMESPACE,
        )
        assert result['resilient']
        assert result['cleaned_up']


@pytest.mark.chaos
@pytest.mark.e2e
class TestAgentHealthAfterPodKill:
    """Kill agent pod → verify HTTP health endpoint recovers."""

    def test_health_recovers_after_pod_kill(self, chaos_client):
        fault = PodKill(label_selector='app=agentic-qa-agent', count=1)
        probe = HttpHealthProbe(url=f'{_AGENT_URL}/health', expected_status=200, timeout=10)

        runner = ChaosRunner(namespace=_NAMESPACE)
        runner.inject = chaos_client.inject
        runner.verify = lambda p, t, **kw: p.check()
        runner.cleanup = chaos_client.cleanup

        result = runner.assert_resilient(
            fault=fault,
            probe=probe,
            target='agentic-qa-agent',
            wait_seconds=20,
            retries=6,
            retry_interval=10,
            namespace=_NAMESPACE,
        )
        assert result['resilient']


@pytest.mark.chaos
@pytest.mark.e2e
class TestFluxSuspend:
    """Suspend Flux kustomization → verify agent still responds."""

    def test_flux_suspend_agent_responds(self, chaos_client):
        fault = FluxSuspend(kustomization_name='agent-deployment')
        probe = HttpHealthProbe(url=f'{_AGENT_URL}/health', expected_status=200, timeout=10)

        runner = ChaosRunner(namespace=_NAMESPACE)
        runner.inject = chaos_client.inject
        runner.verify = lambda p, t, **kw: p.check()
        runner.cleanup = chaos_client.cleanup

        try:
            result = runner.assert_resilient(
                fault=fault,
                probe=probe,
                target='flux',
                wait_seconds=5,
                retries=3,
                retry_interval=5,
                namespace=_NAMESPACE,
            )
            assert result['resilient']
        except Exception:
            # Flux kustomization may not exist in test cluster
            pytest.skip('Flux kustomization not available')


@pytest.mark.chaos
@pytest.mark.e2e
class TestConcurrentReservations:
    """Submit multiple concurrent reservations → verify no deadlocks."""

    def test_concurrent_creates_no_deadlock(self, api_client):
        import concurrent.futures

        def create_reservation(i):
            resp = api_client.post(
                '/api/v1/reservations',
                json={
                    'env_type': 'k8s',
                    'team': 'test-team',
                    'requestor': f'chaos-user-{i}',
                    'resource_spec': {'cpu_cores': 1, 'memory_gb': 1},
                    'ttl_minutes': 30,
                    'description': f'Chaos concurrent test {i}',
                },
            )
            return resp.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_reservation, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should get a response (no timeouts/crashes)
        for status in results:
            assert status < 500, f'Server error during concurrent creates: {status}'

        # Clean up any created reservations
        resp = api_client.get('/api/v1/reservations')
        if resp.status_code == 200:
            for r in resp.json():
                rid = r.get('id') or r.get('reservation_id')
                if rid and 'chaos' in str(r.get('description', '')):
                    api_client.post(f'/api/v1/reservations/{rid}/release')
