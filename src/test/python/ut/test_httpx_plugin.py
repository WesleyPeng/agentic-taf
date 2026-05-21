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

from taf.foundation.plugins.svc.httpx.httpclient import HttpClient
from taf.foundation.plugins.svc.httpx.httpxrestplugin import HttpxRESTPlugin
from taf.foundation.api.plugins import RESTPlugin


class TestHttpxRESTPlugin(TestCase):
    """Tests for HttpxRESTPlugin registration and client property."""

    def test_is_subclass_of_restplugin(self):
        self.assertTrue(issubclass(HttpxRESTPlugin, RESTPlugin))

    def test_registered_in_plugins(self):
        self.assertIn('httpxrestplugin', RESTPlugin.plugins)

    def test_client_returns_httpclient(self):
        plugin = HttpxRESTPlugin()
        self.assertEqual(plugin.client, HttpClient)


class TestHttpClient(TestCase):
    """Tests for HttpClient (httpx-based REST client)."""

    @patch('httpx.Client')
    def test_init(self, mock_httpx_client):
        client = HttpClient('http://example.com')
        mock_httpx_client.assert_called_once()
        self.assertIn('url', client.params)

    @patch('httpx.Client')
    def test_get(self, mock_httpx_client):
        mock_instance = MagicMock()
        mock_httpx_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_instance.get.return_value = mock_response

        client = HttpClient('http://example.com')
        response = client.get('/api/health')
        mock_instance.get.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('httpx.Client')
    def test_post(self, mock_httpx_client):
        mock_instance = MagicMock()
        mock_httpx_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_instance.post.return_value = mock_response

        client = HttpClient('http://example.com')
        response = client.post('/api/data', json={'key': 'value'})
        mock_instance.post.assert_called_once()
        self.assertEqual(response.status_code, 201)

    @patch('httpx.Client')
    def test_delete(self, mock_httpx_client):
        mock_instance = MagicMock()
        mock_httpx_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_instance.delete.return_value = mock_response

        client = HttpClient('http://example.com')
        response = client.delete('/api/data/1')
        mock_instance.delete.assert_called_once()
        self.assertEqual(response.status_code, 204)

    @patch('httpx.Client')
    def test_context_manager(self, mock_httpx_client):
        mock_instance = MagicMock()
        mock_httpx_client.return_value = mock_instance

        with HttpClient('http://example.com') as client:
            self.assertIsInstance(client, HttpClient)
        mock_instance.close.assert_called_once()
