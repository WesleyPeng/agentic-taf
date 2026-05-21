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
