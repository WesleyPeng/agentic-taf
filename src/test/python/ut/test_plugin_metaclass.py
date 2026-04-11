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

import unittest

from taf.foundation.api.plugins.baseplugin import BasePlugin
from taf.foundation.api.plugins import WebPlugin, RESTPlugin, CLIPlugin


class TestBasePluginMetaclass(unittest.TestCase):
    """Test the BasePlugin metaclass registration mechanism."""

    def test_baseplugin_is_metaclass(self):
        self.assertIsInstance(BasePlugin, type)

    def test_webplugin_uses_baseplugin_metaclass(self):
        self.assertIsInstance(WebPlugin, BasePlugin)

    def test_restplugin_uses_baseplugin_metaclass(self):
        self.assertIsInstance(RESTPlugin, BasePlugin)

    def test_cliplugin_uses_baseplugin_metaclass(self):
        self.assertIsInstance(CLIPlugin, BasePlugin)

    def test_plugin_has_plugins_registry(self):
        self.assertTrue(hasattr(WebPlugin, 'plugins'))
        self.assertIsInstance(WebPlugin.plugins, dict)

    def test_webplugin_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            WebPlugin().controls

        with self.assertRaises(NotImplementedError):
            WebPlugin().browser

    def test_restplugin_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            RESTPlugin().client

    def test_cliplugin_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            CLIPlugin().client


class TestPluginMetaclassRegistration(unittest.TestCase):
    """Test that the metaclass properly registers subclasses."""

    def test_dynamic_subclass_registers(self):
        # Create a dynamic subclass of WebPlugin
        DummyPlugin = type.__new__(
            BasePlugin, 'DummyPlugin', (WebPlugin,),
            {'controls': property(lambda self: []),
             'browser': property(lambda self: None)}
        )
        BasePlugin.__init__(
            DummyPlugin, 'DummyPlugin', (WebPlugin,),
            {'controls': property(lambda self: []),
             'browser': property(lambda self: None)}
        )

        self.assertIn('dummyplugin', WebPlugin.plugins)
        # Clean up
        if 'dummyplugin' in WebPlugin.plugins:
            del WebPlugin.plugins['dummyplugin']


if __name__ == '__main__':
    unittest.main()
