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
