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

import socket


class Client:
    def __init__(
            self,
            hostname,
            port=22,
            username=None,
            password=None,
            timeout=30,
            **kwargs
    ):
        kwargs.update(
            hostname=hostname or socket.gethostname(),
            port=port or 22,
            username=username or 'root',
            password=password,
            timeout=timeout
        )

        self.params = kwargs

    def run_command(self, command, *args):
        raise NotImplementedError(
            'Run CLI command'
        )

    def run_commands(self, *commands):
        raise NotImplementedError(
            'Run CLI commands'
        )
