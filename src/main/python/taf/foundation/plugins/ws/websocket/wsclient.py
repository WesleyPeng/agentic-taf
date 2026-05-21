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
