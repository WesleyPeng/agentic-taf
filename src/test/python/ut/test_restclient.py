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

from taf.foundation.plugins.svc.requests \
    import RESTClient as requestsClient
from taf.foundation.utils import YAMLData
from taf.modeling.svc import RESTClient


class TestRESTClient(TestCase):
    def setUp(self):
        self.base_url = 'http://httpbin.org'

    @patch('requests.Session.get')
    def test_rest_get(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{"origin": "127.0.0.1"}'
        mock_get.return_value = mock_response

        with RESTClient(
                self.base_url
        ) as client:
            self.assertIsInstance(
                client,
                requestsClient
            )

            response = client.get('ip')
            self.assertTrue(
                response.ok
            )

            model = client.decode(response.content)

            self.assertIsInstance(
                model,
                YAMLData
            )

            self.assertTrue(
                hasattr(model, 'origin')
            )

            self.assertEqual(
                model.origin,
                '127.0.0.1'
            )
