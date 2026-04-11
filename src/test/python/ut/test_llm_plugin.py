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

_has_langchain = importlib.util.find_spec('langchain_anthropic') is not None


class TestLLMJudgePlugin(TestCase):
    """Tests for LLMJudgePlugin registration and client property."""

    @skipUnless(_has_langchain, 'langchain-anthropic not installed')
    def test_is_subclass_of_llmplugin(self):
        from taf.foundation.plugins.llm.judge.llmjudgeplugin import LLMJudgePlugin
        self.assertTrue(issubclass(LLMJudgePlugin, LLMPlugin))

    @skipUnless(_has_langchain, 'langchain-anthropic not installed')
    def test_registered_in_plugins(self):
        self.assertIn('llmjudgeplugin', LLMPlugin.plugins)

    @skipUnless(_has_langchain, 'langchain-anthropic not installed')
    def test_client_returns_llmclient(self):
        from taf.foundation.plugins.llm.judge.llmjudgeplugin import LLMJudgePlugin
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        plugin = LLMJudgePlugin()
        self.assertEqual(plugin.client, LLMClient)


@skipUnless(_has_langchain, 'langchain-anthropic not installed')
class TestLLMClient(TestCase):
    """Tests for LLMClient (langchain-anthropic based LLM judge)."""

    @patch('taf.foundation.plugins.llm.judge.llmclient.ChatAnthropic')
    def test_init_default_model(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient()
        mock_chat.assert_called_once()
        self.assertEqual(len(client.rubric), 5)

    @patch('taf.foundation.plugins.llm.judge.llmclient.ChatAnthropic')
    def test_init_custom_model(self, mock_chat):
        from taf.foundation.plugins.llm.judge.llmclient import LLMClient
        client = LLMClient(model='claude-3-haiku-20240307')
        self.assertEqual(client.model, 'claude-3-haiku-20240307')

    @patch('taf.foundation.plugins.llm.judge.llmclient.ChatAnthropic')
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
        mock_llm.invoke.assert_called_once()

    @patch('taf.foundation.plugins.llm.judge.llmclient.ChatAnthropic')
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

    @patch('taf.foundation.plugins.llm.judge.llmclient.ChatAnthropic')
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
        self.assertIn('accuracy', scores)
        self.assertIn('completeness', scores)
        self.assertIn('relevance', scores)
        self.assertIn('clarity', scores)
        self.assertIn('safety', scores)
        self.assertIn('overall', scores)
        self.assertEqual(scores['overall'], 4.0)
