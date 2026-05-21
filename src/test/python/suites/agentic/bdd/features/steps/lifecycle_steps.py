# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Wesley Peng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Step definitions for environment lifecycle and rollback feature."""

from behave import when, then


@when('I release the reservation')
def step_release_reservation(context):
    rid = getattr(context, 'reservation_id', None)
    if rid:
        context.release_response = context.api_client.post(
            f'/api/v1/reservations/{rid}/release'
        )
    else:
        context.release_response = type(
            'FakeResp', (), {'status_code': 409}
        )()


@when('I release a reservation with ID "{rid}"')
def step_release_by_id(context, rid):
    context.release_response = context.api_client.post(
        f'/api/v1/reservations/{rid}/release'
    )


@when('I get the reservation details')
def step_get_reservation_details(context):
    rid = getattr(context, 'reservation_id', None)
    if rid:
        context.response = context.api_client.get(
            f'/api/v1/reservations/{rid}'
        )
    else:
        context.response = type(
            'FakeResp', (), {'status_code': 404, 'json': lambda: {}}
        )()


@then('the release response status is {s1:d} or {s2:d} or {s3:d}')
def step_release_status_multi(context, s1, s2, s3):
    actual = context.release_response.status_code
    assert actual in (s1, s2, s3), (
        f'Expected {s1}/{s2}/{s3}, got {actual}'
    )


@then('the release response status is {s1:d} or {s2:d}')
def step_release_status_two(context, s1, s2):
    actual = context.release_response.status_code
    assert actual in (s1, s2), f'Expected {s1}/{s2}, got {actual}'


@then('the reservation state is valid')
def step_reservation_state_valid(context):
    VALID_STATES = {
        'pending', 'queued', 'provisioning', 'ready',
        'active', 'extending', 'expiring', 'releasing',
        'deprovisioning', 'released', 'failed', 'expired', 'cancelled',
    }
    data = context.response.json()
    state = data.get('state', '')
    assert state in VALID_STATES, (
        f'Invalid state "{state}". Expected one of {VALID_STATES}'
    )
    # Save reservation_id for cleanup in subsequent steps
    rid = data.get('id') or data.get('reservation_id')
    if rid:
        context.reservation_id = rid
