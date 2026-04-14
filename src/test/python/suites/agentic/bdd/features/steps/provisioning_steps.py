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

"""Step definitions for environment provisioning feature."""

from behave import given, when, then

from taf.foundation.plugins.svc.httpx import HttpClient


@given('the agent API is accessible')
def step_agent_accessible(context):
    resp = context.api_client.get('/health')
    assert resp.status_code == 200, f'Agent not accessible: {resp.status_code}'


@when('I request the list of reservations')
def step_list_reservations(context):
    context.response = context.api_client.get('/api/v1/reservations')


@when('I create a K8s reservation with TTL {ttl:d} minutes')
def step_create_reservation(context, ttl):
    context.response = context.api_client.post(
        '/api/v1/reservations',
        json={
            'env_type': 'k8s',
            'team': 'test-team',
            'requestor': 'bdd-testuser',
            'resource_spec': {'cpu_cores': 2, 'memory_gb': 4},
            'ttl_minutes': ttl,
            'description': 'BDD test — auto-release',
        },
    )


@when('I request reservations with role "{role}"')
def step_request_with_role(context, role):
    import os
    base_url = os.environ.get('AGENT_BASE_URL', 'http://localhost:18000')
    with HttpClient(
        base_url,
        headers={'X-User': 'u', 'X-Team': 't', 'X-Role': role},
        timeout=10,
    ) as client:
        context.response = client.get('/api/v1/reservations')


@then('the response status is {status:d}')
def step_check_status(context, status):
    assert context.response.status_code == status, (
        f'Expected {status}, got {context.response.status_code}'
    )


@then('the response status is {s1:d} or {s2:d} or {s3:d}')
def step_check_status_multi(context, s1, s2, s3):
    assert context.response.status_code in (s1, s2, s3), (
        f'Expected {s1}/{s2}/{s3}, got {context.response.status_code}'
    )


@then('the response is a list')
def step_response_is_list(context):
    assert isinstance(context.response.json(), list)


@then('the reservation has an ID if created')
def step_reservation_has_id(context):
    if context.response.status_code in (200, 201):
        data = context.response.json()
        rid = data.get('id') or data.get('reservation_id')
        assert rid, f'No reservation ID: {data}'
        # Clean up
        context.api_client.post(f'/api/v1/reservations/{rid}/release')


@then('the response contains "{key}"')
def step_response_contains_key(context, key):
    data = context.response.json()
    assert key in data, f'"{key}" not in {data}'
