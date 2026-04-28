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

"""Shared fixtures for Agentic QA Platform E2E test suites.

Uses ServiceLocator with config override to resolve HttpClient
from the httpx plugin — proves the full discovery chain works:
  config.yml + env override → ServiceLocator → HttpxRESTPlugin → HttpClient

Also exposes the LLM judge fixtures here (T.10.2) so non-AI suites
(chaos, security, BDD) can opt in to quality-based assertions:

- ``llm_judge`` — skips the test if langchain unavailable (AI suite default)
- ``llm_judge_optional`` — returns ``None`` if unavailable (opt-in pattern
  for non-AI suites: ``if llm_judge_optional: ...``)
- ``chat_and_judge`` — composite fixture for the common pattern of sending
  a chat message then optionally evaluating the response
"""

import importlib.util
import os

import pytest
import yaml

from taf.foundation.api.plugins import LLMPlugin, RESTPlugin

from ._fixtures import ConfigurationFixture


_HAS_LANGCHAIN = (
    importlib.util.find_spec('langchain_openai') is not None
    or importlib.util.find_spec('langchain_anthropic') is not None
)


_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')


def _load_config():
    env = os.environ.get('TAF_ENV', 'preprod')
    config_path = os.path.join(_CONFIG_DIR, f'{env}.yml')
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    if os.environ.get('AGENT_BASE_URL'):
        cfg['agent']['base_url'] = os.environ['AGENT_BASE_URL']

    return cfg


def _configure_httpx_plugin():
    """Switch REST plugin to httpx via env overrides, then resolve via ServiceLocator.

    Uses :class:`ConfigurationFixture` to handle the env-set +
    singleton-reset + resolve + type-validate sequence.
    """
    from taf.foundation.plugins.svc.httpx import HttpClient

    return ConfigurationFixture.resolve(
        plugin_interface=RESTPlugin,
        expected_client_cls=HttpClient,
        env_overrides={
            'TAF_PLUGIN_REST_NAME': 'HttpxRESTPlugin',
            'TAF_PLUGIN_REST_LOCATION': '../plugins/svc/httpx',
        },
    )


@pytest.fixture(scope='session')
def config():
    return _load_config()


@pytest.fixture(scope='session')
def agent_url(config):
    return config['agent']['base_url']


@pytest.fixture(scope='session')
def auth_headers(config):
    """Default auth headers for API requests."""
    return {
        'X-User': config['auth']['default_user'],
        'X-Team': config['auth']['default_team'],
        'X-Role': config['auth']['roles']['developer'],
    }


@pytest.fixture(scope='session')
def rest_client_cls():
    """Resolve HttpClient via ServiceLocator with config override.

    This validates that the ServiceLocator correctly discovers
    HttpxRESTPlugin and returns HttpClient as the client class.
    """
    return _configure_httpx_plugin()


@pytest.fixture(scope='session')
def api_client(rest_client_cls, agent_url, auth_headers):
    """Session-scoped REST client resolved via ServiceLocator.

    Instantiates the client class discovered by ServiceLocator
    (HttpClient from httpx plugin) with the agent URL and auth headers.
    """
    with rest_client_cls(
        agent_url,
        headers=auth_headers,
        timeout=30,
    ) as client:
        yield client


def auth_headers_for_role(config, role):
    """Build auth headers for a specific role."""
    return {
        'X-User': config['auth']['default_user'],
        'X-Team': config['auth']['default_team'],
        'X-Role': config['auth']['roles'].get(role, role),
    }


# --- LLM Judge fixtures (T.10.2) ---------------------------------------------
#
# Two fixtures provide different opt-in semantics so the same plugin can be
# used by required (AI suite) and optional (chaos/security/BDD) consumers
# without per-suite reimplementation. This honours SoC: each fixture has a
# single, documented contract.


def _configure_llm_plugin():
    """Enable LLM plugin via env override, resolve via ServiceLocator.

    Validates the discovery chain:
        TAF_PLUGIN_LLM_ENABLED=true
            → Configuration → ServiceLocator → LLMJudgePlugin → LLMClient
    """
    from taf.foundation.plugins.llm.judge.llmclient import LLMClient

    return ConfigurationFixture.resolve(
        plugin_interface=LLMPlugin,
        expected_client_cls=LLMClient,
        env_overrides={'TAF_PLUGIN_LLM_ENABLED': 'true'},
    )


@pytest.fixture(scope='session')
def llm_client_cls():
    """Resolve LLMClient via ServiceLocator with config override.

    Skips the test if langchain is not installed. Suites that want
    optional usage should depend on ``llm_judge_optional`` instead.
    """
    if not _HAS_LANGCHAIN:
        pytest.skip('langchain not installed')
    return _configure_llm_plugin()


@pytest.fixture(scope='session')
def llm_judge(llm_client_cls):
    """Required session-scoped LLMJudge.

    Used by the AI suite — the test is skipped when langchain is absent.
    For opt-in usage in non-AI suites (chaos, security, BDD), use
    ``llm_judge_optional`` which returns ``None`` instead of skipping.
    """
    from taf.modeling.llm import LLMJudge
    return LLMJudge()


@pytest.fixture(scope='session')
def llm_judge_optional():
    """Optional session-scoped LLMJudge — returns ``None`` if unavailable.

    Designed for opt-in usage by non-AI suites:

        def test_recovery_quality(api_client, llm_judge_optional):
            # ... chaos injection, recovery assertion ...
            if llm_judge_optional is None:
                return  # No-op when langchain unavailable
            llm_judge_optional.assert_quality(...)

    Never raises; returns ``None`` for both "no langchain" and
    "plugin resolution failed" cases so that suite-level pytest
    collection is not aborted in environments where the LLM stack
    is intentionally absent.
    """
    if not _HAS_LANGCHAIN:
        return None
    try:
        _configure_llm_plugin()
        from taf.modeling.llm import LLMJudge
        return LLMJudge()
    except Exception:  # pragma: no cover — best-effort opt-in
        return None


@pytest.fixture(scope='session')
def chat_and_judge(api_client, llm_judge_optional):
    """Composite fixture: send a chat message and optionally judge the response.

    Returns a callable ``(message, **judge_kwargs) -> (data, scores | None)``.
    When ``judge_kwargs`` is empty or no judge is available, ``scores`` is
    ``None`` and the test continues — useful for chaos/security suites that
    want quality assertions only when the LLM stack is wired up.

    Example::

        def test_health_query(chat_and_judge):
            data, scores = chat_and_judge(
                'what is the health status?',
                rubric=Client.GROUND_TRUTH_RUBRIC,
                dimension_thresholds={'accuracy': 4.0},
            )
            assert data.get('response')
    """
    def _do(message, **judge_kwargs):
        resp = api_client.post('/api/v1/chat', json={'message': message})
        assert resp.status_code == 200, (
            f'Chat failed: {resp.status_code} {resp.text}'
        )
        data = resp.json()
        scores = None
        if llm_judge_optional is not None and judge_kwargs:
            scores = llm_judge_optional.assert_quality(
                prompt=message,
                response=data.get('response', ''),
                **judge_kwargs,
            )
        return data, scores

    return _do
