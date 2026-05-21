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

import os
import tempfile

import paramiko

from taf.foundation.api.cli import Client
from taf.foundation.utils import logger


class SSHClient(
    paramiko.SSHClient, Client
):
    def __init__(
            self, *args, **kwargs
    ):
        paramiko.SSHClient.__init__(self)
        Client.__init__(self, *args, **kwargs)

        self._initialize(**self.params)

    def run_command(self, command, *args):
        if not (command and command.strip()):
            raise ValueError(
                'Invalid command - {}'.format(command)
            )
        else:
            command = '{cmd} {args}'.format(
                cmd=command.strip(),
                args=' '.join(
                    arg.strip() for arg in args
                )
            )

        std_console: tuple[str, ...] = ('',)
        std_in, std_out, std_err = (None, None, None)

        try:
            std_in, std_out, std_err = self.exec_command(
                command,
                timeout=self.params.get('timeout')
            )

            std_console = (
                std_out.read().decode('utf-8', errors='replace'),
                std_err.read().decode('utf-8', errors='replace'),
            )
        except (IOError, paramiko.SSHException) as ex:
            logger.error(str(ex))
        except Exception:
            raise
        else:
            if (len(std_console) > 1) and std_console[-1]:
                logger.debug(
                    '\n[DEBUG|WARN|ERROR] messages '
                    'are redirected to stderr '
                    'while executing the command\n'
                    'stderr: {}'.format(
                        std_console[-1]
                    )
                )
        finally:
            if std_in:
                std_in.close()

            if std_out:
                std_out.close()

            if std_err:
                std_err.close()

        return std_console

    def run_commands(self, *commands):
        for command in commands:
            yield self.run_command(
                command.split()[0],
                *command.split()[1:]
            )

    def _initialize(self, **kwargs):
        # Currently using username / password to perform authentication.
        # Host key file is not applied, and
        # the log file is located at %tmp% (/tmp) folder
        filename = os.path.join(
            tempfile.gettempdir(),
            'SSHClient.log'
        )
        paramiko.util.log_to_file(filename)
        self.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        self.connect(
            **kwargs
        )
