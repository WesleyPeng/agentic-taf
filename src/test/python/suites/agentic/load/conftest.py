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

"""Load test fixtures — reuses parent conftest api_client.

Additional fixtures for WebSocket scale and timing collection.
"""

import os
import importlib

import pytest


_has_websockets = importlib.util.find_spec('websockets') is not None


@pytest.fixture(scope='session')
def ws_url(config):
    """WebSocket endpoint URL from config or env override."""
    base = os.environ.get(
        'AGENT_BASE_URL',
        config['agent']['base_url'],
    )
    # Convert http(s) to ws(s)
    ws_base = base.replace('https://', 'wss://').replace('http://', 'ws://')
    return f'{ws_base}/api/v1/stream'


@pytest.fixture(scope='session')
def has_websockets():
    """Check if websockets library is available."""
    if not _has_websockets:
        pytest.skip('websockets not installed')
    return True
