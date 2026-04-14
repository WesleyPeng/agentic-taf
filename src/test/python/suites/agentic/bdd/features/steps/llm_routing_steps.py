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

"""Step definitions for LLM routing feature."""

from behave import when, then


@when('I check the health endpoint')
def step_check_health(context):
    context.health_response = context.api_client.get('/health')


@when('I check the LLM models endpoint')
def step_check_models(context):
    context.models_response = context.api_client.get('/api/v1/llm/models')


@then('the health status is "{status}"')
def step_health_status(context, status):
    assert context.health_response.status_code == 200
    data = context.health_response.json()
    assert data['status'] == status


@then('there are {count:d} LLM routing tiers')
def step_llm_tiers_count(context, count):
    data = context.health_response.json()
    tiers = data.get('llm_routing', [])
    assert len(tiers) == count, f'Expected {count} tiers, got {len(tiers)}'


@then('each model has tier, name, and label fields')
def step_models_have_fields(context):
    assert context.models_response.status_code == 200
    models = context.models_response.json()
    assert isinstance(models, list)
    assert len(models) >= 3
    for model in models:
        assert 'tier' in model, f'Missing tier in {model}'
        assert 'name' in model, f'Missing name in {model}'
        assert 'label' in model, f'Missing label in {model}'
