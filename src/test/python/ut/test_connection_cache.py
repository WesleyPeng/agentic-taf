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

from unittest import TestCase
from unittest.mock import MagicMock

from taf.foundation.utils.connectioncache import ConnectionCache


class TestConnectionCacheRegister(TestCase):
    """Tests for ConnectionCache.register()."""

    def setUp(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def tearDown(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def test_register_returns_key(self):
        conn = MagicMock()
        key = ConnectionCache.register(conn, 'conn-1')
        self.assertEqual(key, 'conn-1')

    def test_register_sets_current(self):
        conn = MagicMock()
        ConnectionCache.register(conn, 'conn-1')
        cache = ConnectionCache('conn-1')
        self.assertIs(cache.current, conn)

    def test_register_invalid_connection_raises(self):
        with self.assertRaises(ValueError):
            ConnectionCache.register(None, 'conn-1')

    def test_register_auto_generates_key(self):
        conn = MagicMock()
        key = ConnectionCache.register(conn)
        self.assertIsNotNone(key)
        self.assertIn(key, ConnectionCache.conns)

    def test_register_replaces_existing(self):
        conn1 = MagicMock()
        conn2 = MagicMock()
        ConnectionCache.register(conn1, 'conn-1')
        ConnectionCache.register(conn2, 'conn-1')
        cache = ConnectionCache('conn-1')
        self.assertIs(cache.current, conn2)

    def test_register_multiple(self):
        conn1 = MagicMock()
        conn2 = MagicMock()
        ConnectionCache.register(conn1, 'a')
        ConnectionCache.register(conn2, 'b')
        self.assertEqual(len(ConnectionCache.conns), 2)
        self.assertEqual(ConnectionCache.current_key, 'b')


class TestConnectionCacheSwitch(TestCase):
    """Tests for ConnectionCache.switch()."""

    def setUp(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def tearDown(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def test_switch_returns_connection(self):
        conn = MagicMock()
        ConnectionCache.register(conn, 'conn-1')
        cache = ConnectionCache('conn-1')
        result = cache.switch('conn-1')
        self.assertIs(result, conn)

    def test_switch_updates_current_key(self):
        conn1 = MagicMock()
        conn2 = MagicMock()
        ConnectionCache.register(conn1, 'a')
        ConnectionCache.register(conn2, 'b')
        cache = ConnectionCache('b')
        cache.switch('a')
        self.assertEqual(ConnectionCache.current_key, 'a')

    def test_switch_unknown_key_raises(self):
        cache = ConnectionCache()
        with self.assertRaises(ValueError):
            cache.switch('nonexistent')


class TestConnectionCacheClose(TestCase):
    """Tests for ConnectionCache.close() and close_all()."""

    def setUp(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def tearDown(self):
        ConnectionCache.conns.clear()
        ConnectionCache.current_key = None
        ConnectionCache.closed.clear()

    def test_close_removes_connection(self):
        conn = MagicMock()
        conn.quit = MagicMock()
        ConnectionCache.register(conn, 'conn-1')
        cache = ConnectionCache('conn-1')
        cache.close('conn-1')
        self.assertNotIn('conn-1', ConnectionCache.conns)

    def test_close_calls_quit(self):
        conn = MagicMock()
        ConnectionCache.register(conn, 'conn-1')
        cache = ConnectionCache('conn-1')
        cache.close('conn-1')
        conn.quit.assert_called_once()

    def test_close_current_switches_to_last(self):
        conn1 = MagicMock()
        conn2 = MagicMock()
        ConnectionCache.register(conn1, 'a')
        ConnectionCache.register(conn2, 'b')
        cache = ConnectionCache('b')
        cache.close('b')
        self.assertEqual(ConnectionCache.current_key, 'a')

    def test_close_last_sets_none(self):
        conn = MagicMock()
        ConnectionCache.register(conn, 'only')
        cache = ConnectionCache('only')
        cache.close('only')
        self.assertIsNone(ConnectionCache.current_key)

    def test_get_connection(self):
        conn = MagicMock()
        ConnectionCache.register(conn, 'conn-1')
        cache = ConnectionCache('conn-1')
        self.assertIs(cache.get_connection('conn-1'), conn)
        self.assertIsNone(cache.get_connection('nonexistent'))
