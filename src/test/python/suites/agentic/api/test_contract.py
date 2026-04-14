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

"""T.2.1 — Contract tests: validate agent API responses against OpenAPI schema.

Uses HttpClient resolved via ServiceLocator (rest_client_cls fixture).
"""

import json
import os

import pytest


_SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'contract', 'schemas', 'openapi.json'
)


@pytest.fixture(scope='module')
def openapi_schema():
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


@pytest.mark.e2e
class TestOpenAPIContract:

    def test_schema_is_valid(self, openapi_schema):
        assert 'openapi' in openapi_schema
        assert 'paths' in openapi_schema
        assert len(openapi_schema['paths']) >= 15

    def test_health_endpoint_in_schema(self, openapi_schema):
        assert '/health' in openapi_schema['paths']
        assert 'get' in openapi_schema['paths']['/health']

    def test_all_documented_paths_respond(
            self, rest_client_cls, agent_url, openapi_schema
    ):
        """Every GET path (without path params) should return non-5xx."""
        get_paths = [
            p for p, methods in openapi_schema['paths'].items()
            if 'get' in methods and '{' not in p
        ]

        with rest_client_cls(agent_url, timeout=10) as client:
            for path in get_paths:
                resp = client.get(path)
                assert resp.status_code < 500, (
                    f'{path} returned {resp.status_code}'
                )

    def test_live_schema_matches_stored(
            self, rest_client_cls, agent_url, openapi_schema
    ):
        """The live /openapi.json should have the same paths as stored."""
        with rest_client_cls(agent_url, timeout=10) as client:
            resp = client.get('/openapi.json')
            assert resp.status_code == 200
            live = resp.json()
            assert set(live['paths'].keys()) == set(openapi_schema['paths'].keys())
