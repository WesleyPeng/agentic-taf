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

import socket


class Client(object):
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
