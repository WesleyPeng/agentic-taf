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

from taf.foundation.api.plugins.baseplugin import BasePlugin
from taf.foundation.api.plugins import WSPlugin, LLMPlugin


class TestNewPluginInterfaces(TestCase):
    """Tests for WSPlugin and LLMPlugin interfaces added in T.1.3."""

    def test_wsplugin_uses_baseplugin_metaclass(self):
        self.assertIsInstance(WSPlugin, BasePlugin)

    def test_wsplugin_has_plugins_registry(self):
        self.assertTrue(hasattr(WSPlugin, 'plugins'))
        self.assertIsInstance(WSPlugin.plugins, dict)

    def test_wsplugin_client_raises(self):
        with self.assertRaises(NotImplementedError):
            WSPlugin().client

    def test_llmplugin_uses_baseplugin_metaclass(self):
        self.assertIsInstance(LLMPlugin, BasePlugin)

    def test_llmplugin_has_plugins_registry(self):
        self.assertTrue(hasattr(LLMPlugin, 'plugins'))
        self.assertIsInstance(LLMPlugin.plugins, dict)

    def test_llmplugin_client_raises(self):
        with self.assertRaises(NotImplementedError):
            LLMPlugin().client
