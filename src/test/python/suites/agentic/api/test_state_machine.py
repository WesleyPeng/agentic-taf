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

"""T.2.3 — State machine tests: reservation lifecycle against live agent.

Uses the session-scoped `api_client` fixture (HttpClient from httpx plugin).
"""

import time

import pytest


@pytest.mark.e2e
class TestReservationLifecycle:
    """Full reservation lifecycle: create → get → extend → release."""

    def test_list_reservations(self, api_client):
        resp = api_client.get('/api/v1/reservations')
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_and_release_reservation(self, api_client):
        """Create a k8s reservation, verify it exists, then release it."""
        resp = api_client.post(
            '/api/v1/reservations',
            json={
                'env_type': 'k8s',
                'team': 'test-team',
                'requestor': 'testuser',
                'resource_spec': {
                    'cpu_cores': 2,
                    'memory_gb': 4,
                },
                'ttl_minutes': 30,
                'description': 'TAF API test — auto-release',
            },
        )
        assert resp.status_code in (200, 201, 409), (
            f'Create failed: {resp.status_code} {resp.text}'
        )

        if resp.status_code == 409:
            pytest.skip('Reservation conflict — environment busy')

        data = resp.json()
        reservation_id = data.get('id') or data.get('reservation_id')
        assert reservation_id, f'No reservation ID in response: {data}'

        try:
            # Get
            resp = api_client.get(f'/api/v1/reservations/{reservation_id}')
            assert resp.status_code == 200

            time.sleep(2)

            # Extend (may be forbidden depending on role/state)
            resp = api_client.post(
                f'/api/v1/reservations/{reservation_id}/extend',
                json={'minutes': 30},
            )
            assert resp.status_code in (200, 400, 403, 409)
        finally:
            # Release (always cleanup)
            resp = api_client.post(
                f'/api/v1/reservations/{reservation_id}/release',
            )
            assert resp.status_code in (200, 202, 400, 409)

    def test_get_nonexistent_reservation(self, api_client):
        resp = api_client.get('/api/v1/reservations/nonexistent-id-12345')
        assert resp.status_code in (400, 404, 422)

    def test_release_nonexistent_reservation(self, api_client):
        resp = api_client.post('/api/v1/reservations/nonexistent-id-12345/release')
        assert resp.status_code in (400, 404, 422)
