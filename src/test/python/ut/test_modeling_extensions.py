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

from unittest import TestCase
from unittest.mock import MagicMock

from taf.foundation.api.llm import Client
from taf.modeling.ws.wsclient import WSClient
from taf.modeling.llm.llmjudge import LLMJudge


class TestWSClientModeling(TestCase):
    """Tests for WSClient modeling layer enhancements."""

    def test_collect_returns_messages(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()

        responses = iter(['msg1', 'msg2', 'msg3'])

        def mock_receive(timeout=None):
            try:
                return next(responses)
            except StopIteration:
                raise TimeoutError()

        client.receive = mock_receive
        messages = client.collect(timeout=1)
        self.assertEqual(messages, ['msg1', 'msg2', 'msg3'])

    def test_collect_text_concatenates(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()

        responses = iter(['Hello', ' ', 'World'])

        def mock_receive(timeout=None):
            try:
                return next(responses)
            except StopIteration:
                raise TimeoutError()

        client.receive = mock_receive
        text = client.collect_text(timeout=1)
        self.assertEqual(text, 'Hello World')

    def test_collect_text_with_separator(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()

        responses = iter(['line1', 'line2'])

        def mock_receive(timeout=None):
            try:
                return next(responses)
            except StopIteration:
                raise TimeoutError()

        client.receive = mock_receive
        text = client.collect_text(timeout=1, separator='\n')
        self.assertEqual(text, 'line1\nline2')

    def test_collect_respects_max_messages(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()

        call_count = 0

        def mock_receive(timeout=None):
            nonlocal call_count
            call_count += 1
            return f'msg{call_count}'

        client.receive = mock_receive
        messages = client.collect(timeout=1, max_messages=2)
        self.assertEqual(len(messages), 2)

    def test_send_and_receive(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()
        client.send = MagicMock()
        client.receive = MagicMock(return_value='pong')

        result = client.send_and_receive('ping')
        client.send.assert_called_once_with('ping')
        self.assertEqual(result, 'pong')

    def test_collect_empty_on_immediate_timeout(self):
        client = WSClient('ws://localhost:8080')
        client._connection = MagicMock()

        def mock_receive(timeout=None):
            raise TimeoutError()

        client.receive = mock_receive
        messages = client.collect(timeout=0.01)
        self.assertEqual(messages, [])


class TestLLMJudgeModeling(TestCase):
    """Tests for LLMJudge modeling layer enhancements."""

    def test_assert_quality_passes(self):
        judge = LLMJudge()
        judge.evaluate = MagicMock(return_value={
            'accuracy': 4.5, 'completeness': 4.0,
            'relevance': 4.0, 'clarity': 4.0,
            'safety': 5.0, 'overall': 4.3,
        })

        result = judge.assert_quality('prompt', 'response')
        self.assertTrue(result['passed'])
        self.assertEqual(result['overall'], 4.3)

    def test_assert_quality_fails_overall(self):
        judge = LLMJudge()
        judge.evaluate = MagicMock(return_value={
            'accuracy': 2.0, 'completeness': 2.0,
            'relevance': 2.0, 'clarity': 2.0,
            'safety': 2.0, 'overall': 2.0,
        })

        with self.assertRaises(AssertionError) as ctx:
            judge.assert_quality('prompt', 'response')
        self.assertIn('overall 2.00 < 3.5', str(ctx.exception))

    def test_assert_quality_fails_floor(self):
        judge = LLMJudge()
        judge.evaluate = MagicMock(return_value={
            'accuracy': 1.5, 'completeness': 4.0,
            'relevance': 4.0, 'clarity': 4.0,
            'safety': 4.0, 'overall': 3.5,
        })

        with self.assertRaises(AssertionError) as ctx:
            judge.assert_quality(
                'prompt', 'response', fail_any_below=2.0
            )
        self.assertIn('accuracy 1.50 < 2.0 (floor)', str(ctx.exception))

    def test_assert_quality_fails_dimension_threshold(self):
        judge = LLMJudge()
        judge.evaluate = MagicMock(return_value={
            'accuracy': 3.5, 'completeness': 4.0,
            'relevance': 4.0, 'clarity': 4.0,
            'safety': 4.0, 'overall': 3.9,
        })

        with self.assertRaises(AssertionError) as ctx:
            judge.assert_quality(
                'prompt', 'response',
                dimension_thresholds={'accuracy': 4.0},
            )
        self.assertIn('accuracy 3.50 < 4.0', str(ctx.exception))

    def test_assert_quality_no_floor(self):
        judge = LLMJudge()
        judge.evaluate = MagicMock(return_value={
            'accuracy': 1.0, 'completeness': 5.0,
            'relevance': 5.0, 'clarity': 5.0,
            'safety': 5.0, 'overall': 4.2,
        })

        result = judge.assert_quality(
            'prompt', 'response', fail_any_below=None
        )
        self.assertTrue(result['passed'])

    def test_provider_passthrough(self):
        judge = LLMJudge(provider='anthropic', model='claude-3-haiku')
        self.assertEqual(judge.provider, 'anthropic')
        self.assertEqual(judge.model, 'claude-3-haiku')

    def test_base_url_passthrough(self):
        judge = LLMJudge(base_url='http://localhost:11434/v1')
        self.assertEqual(judge.base_url, 'http://localhost:11434/v1')

    def test_domain_rubric_constants_accessible(self):
        """T.10.1: Three domain-specific rubric constants live on Client."""
        self.assertIn('accuracy', Client.GROUND_TRUTH_RUBRIC)
        self.assertIn('completeness', Client.GROUND_TRUTH_RUBRIC)
        self.assertIn('relevance', Client.GROUND_TRUTH_RUBRIC)
        self.assertIn('safety', Client.GROUND_TRUTH_RUBRIC)

        self.assertIn('safety', Client.DEGRADED_MODE_RUBRIC)
        self.assertIn('clarity', Client.DEGRADED_MODE_RUBRIC)

        self.assertIn('safety', Client.ADVERSARIAL_RUBRIC)
        self.assertIn('accuracy', Client.ADVERSARIAL_RUBRIC)

        # Constants must remain distinct objects to avoid accidental
        # cross-contamination if a caller mutates one.
        self.assertIsNot(Client.GROUND_TRUTH_RUBRIC, Client.DEFAULT_RUBRIC)
        self.assertIsNot(Client.DEGRADED_MODE_RUBRIC, Client.DEFAULT_RUBRIC)
        self.assertIsNot(Client.ADVERSARIAL_RUBRIC, Client.DEFAULT_RUBRIC)

    def test_assert_quality_per_call_rubric_override(self):
        """T.10.1: rubric kwarg swaps self.rubric for the call only."""
        judge = LLMJudge()
        captured: dict = {}

        def fake_evaluate(_prompt, _response, context=None):
            captured['rubric'] = dict(judge.rubric)
            return {
                'safety': 4.5, 'accuracy': 4.0,
                'overall': 4.25,
            }

        judge.evaluate = fake_evaluate
        result = judge.assert_quality(
            'prompt', 'response',
            rubric=Client.ADVERSARIAL_RUBRIC,
            overall_threshold=3.0,
            fail_any_below=None,
        )

        # During the call, self.rubric should equal ADVERSARIAL_RUBRIC
        self.assertEqual(captured['rubric'], Client.ADVERSARIAL_RUBRIC)
        self.assertTrue(result['passed'])

    def test_assert_quality_default_rubric_restored_after_override(self):
        """T.10.1: After assert_quality with rubric=, self.rubric reverts."""
        judge = LLMJudge()
        original = judge.rubric
        judge.evaluate = MagicMock(return_value={
            'overall': 4.0,
        })

        judge.assert_quality(
            'prompt', 'response',
            rubric=Client.GROUND_TRUTH_RUBRIC,
            overall_threshold=3.0,
            fail_any_below=None,
        )

        # After the call, rubric must be restored to original
        self.assertIs(judge.rubric, original)

        # And it must still be restored even when the call raises
        judge.evaluate = MagicMock(return_value={
            'overall': 1.0,  # below threshold → AssertionError
        })
        with self.assertRaises(AssertionError):
            judge.assert_quality(
                'prompt', 'response',
                rubric=Client.DEGRADED_MODE_RUBRIC,
                overall_threshold=3.0,
                fail_any_below=None,
            )
        self.assertIs(judge.rubric, original)
