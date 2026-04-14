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

"""T.8 — Security tests: RBAC enforcement, secret exposure, header injection.

Uses the shared conftest.py fixtures (ServiceLocator → HttpClient).
"""

import re

import pytest


# Endpoints that accept POST (write operations)
_WRITE_ENDPOINTS = [
    ('/api/v1/reservations', {
        'env_type': 'k8s',
        'requestor': 'testuser',
        'team': 'test-team',
        'resource_spec': {'cpu_cores': 1, 'memory_gb': 1},
        'ttl_minutes': 30,
    }),
    ('/api/v1/chat', {
        'message': 'what environments are running?',
    }),
]

# Sensitive patterns that should never appear in API responses
_SECRET_PATTERNS = [
    re.compile(r'ghp_[A-Za-z0-9]{36}'),           # GitHub PAT
    re.compile(r'sk-[A-Za-z0-9]{48}'),             # OpenAI API key
    re.compile(r'sk-ant-[A-Za-z0-9]{40,}'),        # Anthropic key
    re.compile(r'password\s*[=:]\s*["\'][^"\']+'),  # password=... or password:...
    re.compile(r'-----BEGIN.*PRIVATE KEY-----'),    # Private keys
]

# Endpoints to scan for secrets
_SCAN_ENDPOINTS = [
    '/health',
    '/api/v1/llm/models',
    '/api/v1/reporting/test-results',
    '/api/v1/reporting/reports',
]


@pytest.mark.e2e
class TestRoleEnforcement:
    """Verify RBAC: viewer cannot POST write endpoints."""

    def test_viewer_cannot_create_reservation(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={'X-User': 'viewer-user', 'X-Team': 'test-team', 'X-Role': 'viewer'},
            timeout=10,
        ) as client:
            resp = client.post(
                '/api/v1/reservations',
                json=_WRITE_ENDPOINTS[0][1],
            )
            assert resp.status_code == 403, (
                f'Viewer should be forbidden from POST /reservations, got {resp.status_code}'
            )

    def test_developer_can_create_reservation(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={'X-User': 'dev-user', 'X-Team': 'test-team', 'X-Role': 'developer'},
            timeout=30,
        ) as client:
            resp = client.post(
                '/api/v1/reservations',
                json=_WRITE_ENDPOINTS[0][1],
            )
            # Developer should be allowed (200/201) or conflict (409)
            assert resp.status_code in (200, 201, 409), (
                f'Developer should be allowed to POST /reservations, got {resp.status_code}'
            )
            # Clean up if created
            if resp.status_code in (200, 201):
                data = resp.json()
                rid = data.get('id') or data.get('reservation_id')
                if rid:
                    client.post(f'/api/v1/reservations/{rid}/release')

    def test_invalid_role_rejected(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={'X-User': 'u', 'X-Team': 't', 'X-Role': 'superadmin'},
            timeout=10,
        ) as client:
            resp = client.get('/api/v1/reservations')
            assert resp.status_code == 400


@pytest.mark.e2e
class TestSecretExposure:
    """Scan API responses for leaked credentials."""

    def test_no_secrets_in_responses(self, api_client):
        for endpoint in _SCAN_ENDPOINTS:
            resp = api_client.get(endpoint)
            body = resp.text
            for pattern in _SECRET_PATTERNS:
                match = pattern.search(body)
                assert match is None, (
                    f'Secret pattern {pattern.pattern} found in {endpoint}: '
                    f'{match.group()[:20]}...'
                )

    def test_no_raw_credentials_in_health(self, api_client):
        """Health endpoint describes auth methods but must not leak actual keys."""
        data = api_client.get('/health').json()
        # "api_key" as auth method descriptor is fine;
        # actual key values (long strings) are not
        for tier in data.get('llm_routing', []):
            assert 'api_key' not in str(tier.get('base_url', '')), (
                f'API key leaked in base_url for tier {tier["name"]}'
            )


@pytest.mark.e2e
class TestHeaderInjection:
    """Test that malicious header values are sanitized."""

    def test_sql_injection_in_user_header(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={
                'X-User': "admin'; DROP TABLE reservations; --",
                'X-Team': 'test-team',
                'X-Role': 'developer',
            },
            timeout=10,
        ) as client:
            resp = client.get('/api/v1/reservations')
            # Should not crash (500); should return 200 or 400
            assert resp.status_code < 500

    def test_xss_in_user_header(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={
                'X-User': '<script>alert("xss")</script>',
                'X-Team': 'test-team',
                'X-Role': 'developer',
            },
            timeout=10,
        ) as client:
            resp = client.get('/api/v1/reservations')
            assert resp.status_code < 500
            # Response should not reflect the script tag
            assert '<script>' not in resp.text

    def test_oversized_header(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={
                'X-User': 'a' * 10000,
                'X-Team': 'test-team',
                'X-Role': 'developer',
            },
            timeout=10,
        ) as client:
            resp = client.get('/api/v1/reservations')
            # Should not crash; 200 or 400/431
            assert resp.status_code < 500
