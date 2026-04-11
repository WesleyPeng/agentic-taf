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

from websockets.sync.client import connect

from taf.foundation.api.ws import Client


class WSClient(Client):
    def __init__(self, url: str, **kwargs):
        super().__init__(url, **kwargs)

    def connect(self):
        self._connection = connect(
            self.url,
            open_timeout=self.params.get('timeout', 10),
            additional_headers=self.params.get('headers'),
        )

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def send(self, message: str | dict) -> None:
        if self._connection is None:
            raise RuntimeError('Not connected')

        if isinstance(message, dict):
            message = self.encode(message)

        self._connection.send(message)

    def receive(self, timeout: float | None = None) -> str:
        if self._connection is None:
            raise RuntimeError('Not connected')

        return str(self._connection.recv(timeout=timeout))
