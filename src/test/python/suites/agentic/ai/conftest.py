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

"""AI test fixtures — resolve LLMClient via ServiceLocator."""

import importlib
import os

import pytest

from taf.foundation.api.plugins import LLMPlugin
from taf.foundation.conf.configuration import Configuration
from taf.foundation import ServiceLocator

_has_langchain = (
    importlib.util.find_spec('langchain_openai') is not None
    or importlib.util.find_spec('langchain_anthropic') is not None
)


def _configure_llm_plugin():
    """Enable LLM plugin via env override, resolve via ServiceLocator."""
    os.environ['TAF_PLUGIN_LLM_ENABLED'] = 'true'

    Configuration._instance = None
    Configuration._settings = None
    ServiceLocator._plugins.pop(LLMPlugin, None)
    ServiceLocator._clients.pop(LLMPlugin, None)

    client_cls = ServiceLocator.get_client(LLMPlugin)
    assert client_cls is not None, 'ServiceLocator failed to resolve LLM plugin'

    from taf.foundation.plugins.llm.judge.llmclient import LLMClient
    assert client_cls is LLMClient, (
        f'Expected LLMClient, got {client_cls}. '
        'ServiceLocator did not resolve to LLM judge plugin.'
    )
    return client_cls


@pytest.fixture(scope='session')
def llm_client_cls():
    """Resolve LLMClient via ServiceLocator with config override.

    Validates the full chain:
    TAF_PLUGIN_LLM_ENABLED=true → Configuration → ServiceLocator
    → LLMJudgePlugin → LLMClient
    """
    if not _has_langchain:
        pytest.skip('langchain not installed')

    return _configure_llm_plugin()


@pytest.fixture(scope='session')
def llm_judge(llm_client_cls):
    """Session-scoped LLMJudge using the modeling layer.

    LLMJudge inherits from the base Client — it uses evaluate()
    and assert_quality() which delegate to the LLMClient resolved
    by ServiceLocator.
    """
    from taf.modeling.llm import LLMJudge
    return LLMJudge()
