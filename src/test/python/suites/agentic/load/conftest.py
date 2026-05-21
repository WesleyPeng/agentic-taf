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
