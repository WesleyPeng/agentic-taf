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

import importlib
from unittest import TestCase, skipUnless
from unittest.mock import patch, MagicMock

from taf.foundation.api.plugins import LLMPlugin
from taf.foundation.api.llm import Client as LLMBaseClient

_has_langchain_openai = importlib.util.find_spec('langchain_openai') is not None
_has_langchain_anthropic = importlib.util.find_spec('langchain_anthropic') is not None
_has_any_langchain = _has_langchain_openai or _has_langchain_anthropic


class TestLLMBaseClientProviders(TestCase):
    """Tests for LLM base client provider constants."""

    def test_provider_constants(self):
        self.assertEqual(LLMBaseClient.PROVIDER_OPENAI, 'openai')
        self.assertEqual(LLMBaseClient.PROVIDER_ANTHROPIC, 'anthropic')

    def test_init_with_provider(self):
        client = LLMBaseClient(provider='anthropic')
        self.assertEqual(client.provider, 'anthropic')

    def test_init_with_base_url(self):
        client = LLMBaseClient(base_url='http://localhost:11434/v1')
        self.assertEqual(client.base_url, 'http://localhost:11434/v1')

    def test_init_default_provider_is_openai(self):
        client = LLMBaseClient()
        self.assertEqual(client.provider, 'openai')


class TestLLMJudgePlugin(TestCase):
    """Tests for LLMJudgePlugin registration and client property."""

    @skipUnless(_has_any_langchain, 'langchain not installed')
    def test_is_subclass_of_llmplugin(self):
        from taf.foundation.plugins.llm.judge.llmjudgeplugin import LLMJudgePlugin
        self.assertTrue(issubclass(LLMJudgePlugin, LLMPlugin))

    @skipUnless(_has_any_langchain, 'langchain not installed')
    def test_registered_in_plugins(self):
        self.assertIn('llmjudgeplugin', LLMPlugin.plugins)

    @skipUnless(_has_any_langchain, 'langchain not installed')
    def test_client_returns_llmclient(self):
        from taf.foundation.plugins.llm.judge.llmjudgeplugin import LLMJudgePlugin
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        plugin = LLMJudgePlugin()
        self.assertEqual(plugin.client, LLMClient)


@skipUnless(_has_langchain_openai, 'langchain-openai not installed')
class TestLLMClientOpenAI(TestCase):
    """Tests for LLMClient with OpenAI provider (default)."""

    @patch('langchain_openai.ChatOpenAI')
    def test_default_provider_is_openai(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient()
        mock_chat.assert_called_once()
        self.assertEqual(client.provider, 'openai')
        self.assertEqual(client.model, 'gpt-4o-mini')

    @patch('langchain_openai.ChatOpenAI')
    def test_custom_base_url(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient(
            base_url='http://localhost:11434/v1',
            model='llama3',
        )
        call_kwargs = mock_chat.call_args[1]
        self.assertEqual(call_kwargs['base_url'], 'http://localhost:11434/v1')
        self.assertEqual(client.model, 'llama3')

    @patch('langchain_openai.ChatOpenAI')
    def test_score(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient

        mock_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.content = '{"score": 4.5, "reason": "accurate"}'
        mock_llm.invoke.return_value = mock_result
        mock_chat.return_value = mock_llm

        client = LLMClient()
        score = client.score('What is 2+2?', 'The answer is 4.', 'accuracy')
        self.assertEqual(score, 4.5)

    @patch('langchain_openai.ChatOpenAI')
    def test_evaluate_all_dimensions(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient

        mock_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.content = '{"score": 4.0, "reason": "good"}'
        mock_llm.invoke.return_value = mock_result
        mock_chat.return_value = mock_llm

        client = LLMClient()
        scores = client.evaluate('prompt', 'response')

        self.assertEqual(len(scores), 6)  # 5 dimensions + overall
        self.assertIn('overall', scores)
        self.assertEqual(scores['overall'], 4.0)

    @patch('langchain_openai.ChatOpenAI')
    def test_score_invalid_response_returns_default(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient

        mock_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.content = 'not json'
        mock_llm.invoke.return_value = mock_result
        mock_chat.return_value = mock_llm

        client = LLMClient()
        score = client.score('prompt', 'response', 'accuracy')
        self.assertEqual(score, 3.0)


@skipUnless(_has_langchain_anthropic, 'langchain-anthropic not installed')
class TestLLMClientAnthropic(TestCase):
    """Tests for LLMClient with Anthropic provider."""

    @patch('langchain_anthropic.ChatAnthropic')
    def test_anthropic_provider(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient(provider='anthropic')
        mock_chat.assert_called_once()
        self.assertEqual(client.provider, 'anthropic')
        self.assertEqual(client.model, 'claude-sonnet-4-20250514')

    @patch('langchain_anthropic.ChatAnthropic')
    def test_anthropic_score(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient

        mock_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.content = '{"score": 4.0, "reason": "ok"}'
        mock_llm.invoke.return_value = mock_result
        mock_chat.return_value = mock_llm

        client = LLMClient(provider='anthropic')
        score = client.score('prompt', 'response', 'accuracy')
        self.assertEqual(score, 4.0)


@skipUnless(_has_langchain_openai, 'langchain-openai not installed')
class TestLLMClientEnvOverride(TestCase):
    """Tests for TAF_LLM_PROVIDER env var override."""

    @patch('langchain_openai.ChatOpenAI')
    @patch.dict('os.environ', {'TAF_LLM_PROVIDER': 'openai'})
    def test_env_var_openai(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient()
        self.assertEqual(client.provider, 'openai')
