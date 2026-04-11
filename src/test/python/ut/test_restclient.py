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
