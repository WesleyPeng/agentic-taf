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

from taf.foundation.api.ws import Client


class WSClient(Client):
    """High-level WebSocket client with streaming support.

    Usage::

        with WSClient('ws://localhost:8080/ws') as ws:
            ws.send({'type': 'chat', 'message': 'hello'})

            # Collect all messages until timeout
            messages = ws.collect(timeout=5)

            # Or iterate token-by-token
            ws.send({'type': 'stream'})
            full = ws.collect_text(timeout=10)
    """

    def collect(
            self,
            timeout: float = 5.0,
            max_messages: int = 100,
    ) -> list[str]:
        """Receive messages until timeout or max_messages reached."""
        messages: list[str] = []
        for _ in range(max_messages):
            try:
                msg = self.receive(timeout=timeout)
                messages.append(msg)
            except Exception:
                break
        return messages

    def collect_text(
            self,
            timeout: float = 5.0,
            max_messages: int = 100,
            separator: str = '',
    ) -> str:
        """Receive messages and concatenate into a single string."""
        return separator.join(
            self.collect(timeout=timeout, max_messages=max_messages)
        )

    def send_and_receive(
            self,
            message: str | dict,
            timeout: float = 10.0,
    ) -> str:
        """Send a message and return the first response."""
        self.send(message)
        return self.receive(timeout=timeout)
