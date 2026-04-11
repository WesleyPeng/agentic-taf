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

import json
from unittest import TestCase

from taf.foundation.api.ws.client import Client as WSBaseClient
from taf.foundation.api.llm.client import Client as LLMBaseClient


class TestWSBaseClient(TestCase):
    """Tests for the WebSocket base client interface."""

    def test_init(self):
        client = WSBaseClient('ws://localhost:8080')
        self.assertEqual(client.url, 'ws://localhost:8080')
        self.assertIsNone(client._connection)

    def test_connect_raises(self):
        client = WSBaseClient('ws://localhost:8080')
        with self.assertRaises(NotImplementedError):
            client.connect()

    def test_send_raises(self):
        client = WSBaseClient('ws://localhost:8080')
        with self.assertRaises(NotImplementedError):
            client.send('hello')

    def test_receive_raises(self):
        client = WSBaseClient('ws://localhost:8080')
        with self.assertRaises(NotImplementedError):
            client.receive()

    def test_close_raises(self):
        client = WSBaseClient('ws://localhost:8080')
        with self.assertRaises(NotImplementedError):
            client.close()

    def test_encode(self):
        result = WSBaseClient.encode({'type': 'ping'})
        self.assertEqual(json.loads(result), {'type': 'ping'})

    def test_decode_valid_json(self):
        result = WSBaseClient.decode('{"type": "pong"}')
        self.assertEqual(result, {'type': 'pong'})

    def test_decode_invalid_json(self):
        result = WSBaseClient.decode('not json')
        self.assertEqual(result, {'raw': 'not json'})

    def test_context_manager_protocol(self):
        # Verify __enter__ and __exit__ exist
        client = WSBaseClient('ws://localhost:8080')
        self.assertTrue(hasattr(client, '__enter__'))
        self.assertTrue(hasattr(client, '__exit__'))


class TestLLMBaseClient(TestCase):
    """Tests for the LLM base client interface."""

    def test_init_defaults(self):
        client = LLMBaseClient()
        self.assertIsNone(client.model)
        self.assertEqual(len(client.rubric), 5)
        self.assertIn('accuracy', client.rubric)
        self.assertIn('completeness', client.rubric)
        self.assertIn('relevance', client.rubric)
        self.assertIn('clarity', client.rubric)
        self.assertIn('safety', client.rubric)

    def test_init_custom_rubric(self):
        custom = {'correctness': 'Is the answer correct'}
        client = LLMBaseClient(rubric=custom)
        self.assertEqual(client.rubric, custom)

    def test_init_with_model(self):
        client = LLMBaseClient(model='claude-sonnet-4-20250514')
        self.assertEqual(client.model, 'claude-sonnet-4-20250514')

    def test_evaluate_raises(self):
        client = LLMBaseClient()
        with self.assertRaises(NotImplementedError):
            client.evaluate('prompt', 'response')

    def test_score_raises(self):
        client = LLMBaseClient()
        with self.assertRaises(NotImplementedError):
            client.score('prompt', 'response', 'accuracy')
