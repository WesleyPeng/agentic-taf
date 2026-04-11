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

from taf.foundation.api.ws import Client


class WSClient(Client):
    """High-level WebSocket client.

    Usage via ServiceLocator when WSPlugin is enabled in config,
    or directly for standalone WebSocket testing:

        with WSClient('ws://localhost:8080/ws') as ws:
            ws.send({'type': 'ping'})
            response = ws.receive(timeout=5)
    """
    pass
