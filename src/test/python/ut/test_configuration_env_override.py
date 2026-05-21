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
import unittest

from taf.foundation.conf import Configuration


class TestConfigurationEnvOverride(unittest.TestCase):
    """Test environment variable overrides for plugin configuration."""

    def setUp(self):
        # Reset singleton so each test gets a fresh Configuration
        Configuration._instance = None
        Configuration._settings = None

    def tearDown(self):
        # Clean up env vars
        for key in list(os.environ.keys()):
            if key.startswith('TAF_PLUGIN_'):
                del os.environ[key]
        # Reset singleton
        Configuration._instance = None
        Configuration._settings = None

    def test_env_override_disables_plugin(self):
        os.environ['TAF_PLUGIN_MOBILE_ENABLED'] = 'false'
        conf = Configuration.get_instance()

        mobile_plugin = vars(conf.plugins).get('mobile')
        self.assertIsNotNone(mobile_plugin)
        self.assertFalse(mobile_plugin.enabled)

    def test_env_override_enables_plugin(self):
        os.environ['TAF_PLUGIN_MOBILE_ENABLED'] = 'true'
        conf = Configuration.get_instance()

        mobile_plugin = vars(conf.plugins).get('mobile')
        self.assertIsNotNone(mobile_plugin)
        self.assertTrue(mobile_plugin.enabled)

    def test_env_override_changes_location(self):
        os.environ['TAF_PLUGIN_WEB_LOCATION'] = '../plugins/web/playwright'
        conf = Configuration.get_instance()

        web_plugin = vars(conf.plugins).get('web')
        self.assertEqual(web_plugin.location, '../plugins/web/playwright')

    def test_env_override_ignores_unknown_plugin(self):
        os.environ['TAF_PLUGIN_NONEXISTENT_ENABLED'] = 'true'
        # Should not raise
        conf = Configuration.get_instance()
        self.assertIsNotNone(conf.plugins)

    def test_env_override_boolean_parsing(self):
        for true_val in ('true', 'True', 'TRUE', '1', 'yes', 'Yes'):
            Configuration._instance = None
            Configuration._settings = None
            os.environ['TAF_PLUGIN_MOBILE_ENABLED'] = true_val
            conf = Configuration.get_instance()
            mobile = vars(conf.plugins).get('mobile')
            self.assertTrue(
                mobile.enabled,
                f"Expected True for '{true_val}'"
            )

        for false_val in ('false', 'False', '0', 'no', 'anything'):
            Configuration._instance = None
            Configuration._settings = None
            os.environ['TAF_PLUGIN_MOBILE_ENABLED'] = false_val
            conf = Configuration.get_instance()
            mobile = vars(conf.plugins).get('mobile')
            self.assertFalse(
                mobile.enabled,
                f"Expected False for '{false_val}'"
            )

    def test_configuration_singleton_persists(self):
        conf1 = Configuration.get_instance()
        conf2 = Configuration.get_instance()
        self.assertIs(conf1, conf2)


if __name__ == '__main__':
    unittest.main()
