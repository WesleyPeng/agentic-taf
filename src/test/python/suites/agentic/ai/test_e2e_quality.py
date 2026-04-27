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

"""T.10.3 — Ground-truth anchored + multi-turn coherence tests.

These E2E tests use the platform's deterministic REST APIs as ground truth
for evaluating chat-agent response quality. The pattern transforms vague
"is this a good answer?" assessment into precise "does this match known
facts?" assertions — the highest-value LLM-judge usage pattern.

Test classes:
- TestGroundTruthAccuracy (3 tests) — chat responses match deterministic
  API data using ``Client.GROUND_TRUTH_RUBRIC``
- TestMultiTurnCoherence (2 tests) — agent retains context across turns

All tests:
- Marked ``@pytest.mark.ai @pytest.mark.e2e`` (gated by TAF_RUN_E2E
  + TAF_PLUGIN_LLM_ENABLED env vars in CI)
- Use the shared ``llm_judge`` fixture from ``agentic/conftest.py``
- Skip gracefully when langchain not installed (fixture skip)
  or agent LLM backend is down (``_skip_if_llm_unavailable``)
- Re-export ``_chat`` and ``_skip_if_llm_unavailable`` helpers from
  ``test_ai`` to keep behaviour identical between AI test files
"""

import pytest

from taf.foundation.api.llm import Client

from .test_ai import _chat, _skip_if_llm_unavailable


# --- Ground-truth anchored evaluation ---

@pytest.mark.ai
@pytest.mark.e2e
class TestGroundTruthAccuracy:
    """Verify chat responses match data from deterministic REST APIs."""

    def test_health_status_accuracy(self, api_client, llm_judge):
        """Agent health description must match GET /health output."""
        health = api_client.get('/health').json()
        prompt = 'what is the platform health status?'
        result = _chat(api_client, prompt)
        _skip_if_llm_unavailable(result)

        llm_judge.assert_quality(
            prompt=prompt,
            response=result['response'],
            context=health,
            rubric=Client.GROUND_TRUTH_RUBRIC,
            dimension_thresholds={'accuracy': 4.0},
            fail_any_below=2.0,
        )

    def test_reservation_list_accuracy(self, api_client, llm_judge):
        """Agent's reservation summary must match GET /api/v1/reservations."""
        reservations = api_client.get('/api/v1/reservations').json()
        prompt = 'list all active reservations'
        result = _chat(api_client, prompt)
        _skip_if_llm_unavailable(result)

        llm_judge.assert_quality(
            prompt=prompt,
            response=result['response'],
            context={
                'reservations': reservations,
                'count': len(reservations) if isinstance(reservations, list)
                else len(reservations.get('items', [])),
            },
            rubric=Client.GROUND_TRUTH_RUBRIC,
            dimension_thresholds={'accuracy': 3.5},
            fail_any_below=2.0,
        )

    def test_llm_models_accuracy(self, api_client, llm_judge):
        """Agent's model listing must match GET /api/v1/llm/models."""
        models = api_client.get('/api/v1/llm/models').json()
        prompt = 'what LLM models are available?'
        result = _chat(api_client, prompt)
        _skip_if_llm_unavailable(result)

        # Default rubric is fine here — all 5 dimensions are relevant
        llm_judge.assert_quality(
            prompt=prompt,
            response=result['response'],
            context={
                'models': models,
                'count': len(models) if isinstance(models, list)
                else len(models.get('items', [])),
            },
            dimension_thresholds={'accuracy': 3.5, 'completeness': 3.0},
            fail_any_below=2.0,
        )


# --- Multi-turn coherence ---

@pytest.mark.ai
@pytest.mark.e2e
class TestMultiTurnCoherence:
    """Verify the agent maintains context across conversation turns."""

    def test_provision_then_status_coherence(self, api_client, llm_judge):
        """After requesting provision, agent's status follow-up references same env."""
        prompt_1 = 'I need a K8s environment for testing'
        r1 = _chat(api_client, prompt_1)
        _skip_if_llm_unavailable(r1)
        thread_id = r1.get('thread_id')

        # Follow-up in the same thread to test context retention
        prompt_2 = 'what is the status of that environment?'
        body = {'message': prompt_2}
        if thread_id:
            body['thread_id'] = thread_id
        r2 = api_client.post('/api/v1/chat', json=body).json()
        _skip_if_llm_unavailable(r2)

        llm_judge.assert_quality(
            prompt=prompt_2,
            response=r2['response'],
            context={'prior_response': r1['response']},
            dimension_thresholds={'relevance': 3.5, 'accuracy': 3.0},
            fail_any_below=2.0,
        )

    def test_agent_remembers_team(self, api_client, llm_judge):
        """Agent retains team context from prior message."""
        prompt_1 = 'I am from the payments team'
        r1 = _chat(api_client, prompt_1)
        _skip_if_llm_unavailable(r1)
        thread_id = r1.get('thread_id')

        prompt_2 = 'what environments does my team have?'
        body = {'message': prompt_2}
        if thread_id:
            body['thread_id'] = thread_id
        r2 = api_client.post('/api/v1/chat', json=body).json()
        _skip_if_llm_unavailable(r2)

        llm_judge.assert_quality(
            prompt=prompt_2,
            response=r2['response'],
            context={'expected_team': 'payments'},
            dimension_thresholds={'relevance': 3.5},
            fail_any_below=2.0,
        )
