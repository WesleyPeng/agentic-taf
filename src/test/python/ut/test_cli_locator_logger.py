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
from unittest import TestCase

from taf.foundation.api.cli.client import Client
from taf.foundation.api.ui.support.locator import Locator
from taf.foundation.utils.logger import _logger


class TestCLIBaseClient(TestCase):
    """Tests for CLI base client initialization."""

    def test_init_default_port(self):
        client = Client('example.com')
        self.assertEqual(client.params['hostname'], 'example.com')
        self.assertEqual(client.params['port'], 22)

    def test_init_custom_port(self):
        client = Client('host', port=2222)
        self.assertEqual(client.params['port'], 2222)

    def test_init_default_username(self):
        client = Client('host')
        self.assertEqual(client.params['username'], 'root')

    def test_init_custom_credentials(self):
        client = Client('host', username='admin', password='secret')
        self.assertEqual(client.params['username'], 'admin')
        self.assertEqual(client.params['password'], 'secret')

    def test_init_default_timeout(self):
        client = Client('host')
        self.assertEqual(client.params['timeout'], 30)

    def test_init_none_hostname_uses_local(self):
        client = Client(None)
        self.assertEqual(client.params['hostname'], socket.gethostname())

    def test_init_kwargs_forwarded(self):
        client = Client('host', key_filename='/path/to/key')
        self.assertEqual(client.params['key_filename'], '/path/to/key')

    def test_run_command_raises(self):
        client = Client('host')
        with self.assertRaises(NotImplementedError):
            client.run_command('ls')

    def test_run_commands_raises(self):
        client = Client('host')
        with self.assertRaises(NotImplementedError):
            client.run_commands('ls', 'pwd')


class TestLocator(TestCase):
    """Tests for Locator enum."""

    def test_unknown_returns_string(self):
        self.assertEqual(Locator.unknown(), 'unknown')

    def test_prioritized_locators_returns_tuple(self):
        result = Locator.prioritized_locators()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 0)

    def test_is_str_enum(self):
        self.assertTrue(issubclass(Locator, str))


class TestLogger(TestCase):
    """Tests for logger utility."""

    def test_returns_logger(self):
        import logging
        log = _logger('test_logger_unit')
        self.assertIsInstance(log, logging.Logger)

    def test_default_name(self):
        log = _logger()
        self.assertIsNotNone(log.name)

    def test_custom_name(self):
        log = _logger('custom_name')
        self.assertEqual(log.name, 'custom_name')

    def test_has_handler(self):
        log = _logger('handler_test')
        self.assertGreaterEqual(len(log.handlers), 1)

    def test_idempotent_handler(self):
        log1 = _logger('idempotent_test')
        count1 = len(log1.handlers)
        log2 = _logger('idempotent_test')
        count2 = len(log2.handlers)
        self.assertEqual(count1, count2)
