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

from unittest import TestCase
from unittest import skip

from taf.foundation.plugins.cli.paramiko import SSHClient
from taf.modeling.cli import CLIRunner


@skip('Temporarily ignore CLI tests')
class TestCLIRunner(TestCase):
    def setUp(self):
        self.hostname = 'localhost'
        self.username = 'username'
        self.password = 'password'

    def test_run_command(self):
        with CLIRunner(
            hostname=self.hostname,
            username=self.username,
            password=self.password
        ) as runner:
            self.assertIsInstance(
                runner,
                SSHClient
            )

            response = runner.run_command(
                'ls', '-lat'
            )
            self.assertEqual(
                len(response),
                2
            )
            self.assertEqual(
                response[-1],
                ''
            )
            self.assertIn(
                self.username,
                response[0]
            )
