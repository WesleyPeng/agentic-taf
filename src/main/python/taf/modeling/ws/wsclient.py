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
