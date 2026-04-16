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

import os
from unittest import TestCase

from taf.foundation.api.plugins.baseplugin import BasePlugin
from taf.foundation.api.plugins import (
    WebPlugin, RESTPlugin, CLIPlugin, WSPlugin,
    LLMPlugin,
)
from taf.foundation.api.plugins.mobileplugin import MobilePlugin


class TestBasePluginMetaclass(TestCase):
    """Tests for BasePlugin metaclass registration mechanism."""

    def test_is_type(self):
        self.assertIsInstance(BasePlugin, type)

    def test_has_plugin_path(self):
        self.assertTrue(hasattr(BasePlugin, 'plugin_path'))
        self.assertTrue(os.path.isabs(BasePlugin.plugin_path))

    def test_register_plugin_dir_valid(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            BasePlugin.register_plugin_dir(d)
            self.assertEqual(BasePlugin.plugin_path, d)

    def test_register_plugin_dir_invalid_raises(self):
        with self.assertRaises(AssertionError):
            BasePlugin.register_plugin_dir('/nonexistent/path')


class TestWebPlugin(TestCase):
    """Tests for WebPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(WebPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(WebPlugin, 'plugins'))
        self.assertIsInstance(WebPlugin.plugins, dict)

    def test_controls_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = WebPlugin().controls

    def test_browser_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = WebPlugin().browser

    def test_app_under_test_delegates_to_browser(self):
        with self.assertRaises(NotImplementedError):
            _ = WebPlugin().app_under_test


class TestRESTPlugin(TestCase):
    """Tests for RESTPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(RESTPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(RESTPlugin, 'plugins'))

    def test_client_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = RESTPlugin().client


class TestCLIPlugin(TestCase):
    """Tests for CLIPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(CLIPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(CLIPlugin, 'plugins'))

    def test_client_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = CLIPlugin().client


class TestWSPlugin(TestCase):
    """Tests for WSPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(WSPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(WSPlugin, 'plugins'))

    def test_client_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = WSPlugin().client


class TestLLMPlugin(TestCase):
    """Tests for LLMPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(LLMPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(LLMPlugin, 'plugins'))

    def test_client_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = LLMPlugin().client


class TestMobilePlugin(TestCase):
    """Tests for MobilePlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(MobilePlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(MobilePlugin, 'plugins'))

    def test_controls_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = MobilePlugin().controls

    def test_browser_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = MobilePlugin().browser

    def test_app_under_test_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = MobilePlugin().app_under_test
