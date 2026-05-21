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

from unittest import TestCase
from unittest.mock import patch, MagicMock

from taf.foundation.plugins.ws.websocket.wsclient import WSClient
from taf.foundation.plugins.ws.websocket.websocketplugin import WebSocketPlugin
from taf.foundation.api.plugins import WSPlugin
from taf.foundation.api.ws import Client as WSBaseClient


class TestWebSocketPlugin(TestCase):
    """Tests for WebSocketPlugin registration and client property."""

    def test_is_subclass_of_wsplugin(self):
        self.assertTrue(issubclass(WebSocketPlugin, WSPlugin))

    def test_registered_in_plugins(self):
        self.assertIn('websocketplugin', WSPlugin.plugins)

    def test_client_returns_wsclient(self):
        plugin = WebSocketPlugin()
        self.assertEqual(plugin.client, WSClient)


class TestWSClient(TestCase):
    """Tests for WSClient (websockets-based WebSocket client)."""

    def test_is_subclass_of_base(self):
        self.assertTrue(issubclass(WSClient, WSBaseClient))

    def test_init(self):
        client = WSClient('ws://localhost:8080/ws')
        self.assertEqual(client.url, 'ws://localhost:8080/ws')
        self.assertIsNone(client._connection)

    def test_send_raises_when_not_connected(self):
        client = WSClient('ws://localhost:8080/ws')
        with self.assertRaises(RuntimeError):
            client.send('hello')

    def test_receive_raises_when_not_connected(self):
        client = WSClient('ws://localhost:8080/ws')
        with self.assertRaises(RuntimeError):
            client.receive()

    @patch('taf.foundation.plugins.ws.websocket.wsclient.connect')
    def test_connect_and_send(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        client = WSClient('ws://localhost:8080/ws')
        client.connect()
        mock_connect.assert_called_once()

        client.send('hello')
        mock_conn.send.assert_called_once_with('hello')

    @patch('taf.foundation.plugins.ws.websocket.wsclient.connect')
    def test_connect_and_receive(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.recv.return_value = '{"status": "ok"}'
        mock_connect.return_value = mock_conn

        client = WSClient('ws://localhost:8080/ws')
        client.connect()

        msg = client.receive()
        self.assertEqual(msg, '{"status": "ok"}')

    @patch('taf.foundation.plugins.ws.websocket.wsclient.connect')
    def test_send_dict_encodes_json(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        client = WSClient('ws://localhost:8080/ws')
        client.connect()
        client.send({'type': 'ping'})

        sent = mock_conn.send.call_args[0][0]
        self.assertIn('"type"', sent)
        self.assertIn('"ping"', sent)

    @patch('taf.foundation.plugins.ws.websocket.wsclient.connect')
    def test_close(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        client = WSClient('ws://localhost:8080/ws')
        client.connect()
        client.close()
        mock_conn.close.assert_called_once()
        self.assertIsNone(client._connection)
