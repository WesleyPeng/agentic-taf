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

"""T.2.2 — Functional API tests against live preprod agent.

Uses the session-scoped `api_client` fixture (HttpClient resolved via
ServiceLocator from the httpx plugin) provided by conftest.py.
"""

import pytest


@pytest.mark.e2e
class TestHealthEndpoint:

    def test_health_ok(self, api_client):
        resp = api_client.get('/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'components' in data

    def test_health_components(self, api_client):
        data = api_client.get('/health').json()
        components = data['components']
        assert 'database' in components
        assert 'nats' in components
        assert components['database'] == 'ok'
        assert components['nats'] == 'ok'

    def test_health_llm_routing(self, api_client):
        data = api_client.get('/health').json()
        assert 'llm_routing' in data
        tiers = data['llm_routing']
        assert len(tiers) == 3
        tier_numbers = [t['tier'] for t in tiers]
        assert tier_numbers == [1, 2, 3]


@pytest.mark.e2e
class TestLLMModelsEndpoint:

    def test_models_returns_list(self, api_client):
        resp = api_client.get('/api/v1/llm/models')
        assert resp.status_code == 200
        models = resp.json()
        assert isinstance(models, list)
        assert len(models) >= 3

    def test_models_have_required_fields(self, api_client):
        models = api_client.get('/api/v1/llm/models').json()
        for model in models:
            assert 'tier' in model
            assert 'name' in model
            assert 'label' in model


@pytest.mark.e2e
class TestReportingEndpoints:

    def test_test_results(self, api_client):
        resp = api_client.get('/api/v1/reporting/test-results')
        assert resp.status_code == 200
        data = resp.json()
        assert 'total' in data
        assert 'results' in data

    def test_test_results_summary(self, api_client):
        resp = api_client.get('/api/v1/reporting/test-results/summary')
        assert resp.status_code == 200

    def test_reports(self, api_client):
        resp = api_client.get('/api/v1/reporting/reports')
        assert resp.status_code == 200

    def test_analytics_environments(self, api_client):
        resp = api_client.get('/api/v1/reporting/analytics/environments')
        assert resp.status_code == 200

    def test_analytics_flaky_tests(self, api_client):
        resp = api_client.get('/api/v1/reporting/analytics/flaky-tests')
        assert resp.status_code == 200

    def test_analytics_sonarqube(self, api_client):
        resp = api_client.get('/api/v1/reporting/analytics/sonarqube')
        assert resp.status_code == 200


@pytest.mark.e2e
class TestAuthErrors:

    def test_invalid_role_rejected(self, rest_client_cls, agent_url):
        with rest_client_cls(
            agent_url,
            headers={'X-User': 'u', 'X-Team': 't', 'X-Role': 'admin'},
            timeout=10,
        ) as client:
            resp = client.get('/api/v1/reservations')
            assert resp.status_code == 400
            data = resp.json()
            assert 'detail' in data


@pytest.mark.e2e
class TestMetrics:

    def test_metrics_endpoint(self, api_client):
        resp = api_client.get('/metrics')
        assert resp.status_code == 200
        assert 'http_requests_total' in resp.text or 'process_' in resp.text
