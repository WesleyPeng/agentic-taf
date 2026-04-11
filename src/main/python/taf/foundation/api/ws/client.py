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

import json


from typing import Any


class Client:
    def __init__(
            self,
            url: str,
            **kwargs
    ):
        self.url = url
        self.params = kwargs
        self._connection: Any = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self):
        raise NotImplementedError(
            'Connect to WebSocket server'
        )

    def close(self):
        raise NotImplementedError(
            'Close WebSocket connection'
        )

    def send(self, message: str | dict) -> None:
        raise NotImplementedError(
            'Send message to WebSocket server'
        )

    def receive(self, timeout: float | None = None) -> str:
        raise NotImplementedError(
            'Receive message from WebSocket server'
        )

    @classmethod
    def encode(cls, data: dict) -> str:
        return json.dumps(data)

    @classmethod
    def decode(cls, message: str) -> dict:
        try:
            return json.loads(message)
        except (TypeError, ValueError):
            return {'raw': message}
