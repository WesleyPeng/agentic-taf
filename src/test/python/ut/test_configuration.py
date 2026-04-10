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

from taf.foundation.conf import Configuration
from taf.foundation.utils import YAMLData
# from taf.foundation.utils import logger


class TestConfiguration(TestCase):
    def setUp(self):
        self.conf = Configuration()
        # logger.setLevel('DEBUG')

    def test_configuration(self):
        self.assertIs(
            self.conf.get_instance(),
            Configuration.get_instance()
        )

        self.assertIsInstance(
            Configuration.get_instance().plugins,
            YAMLData
        )

        _conf_file = 'test_config.yml'
        _conf_key = 'test_config_dummy_key'
        _conf_value = 'enabled'

        plugins = Configuration.get_instance().plugins
        plugins += {
            _conf_key: _conf_value
        }

        self.conf.save_as(_conf_file)

        # logger.debug('Validating configuration file')
        self.assertTrue(
            os.path.isfile(_conf_file)
        )
        with open(_conf_file, 'r') as conf:
            for line in conf:
                if (_conf_key in line) and (_conf_value in line):
                    found = True
                    break
            else:
                found = False

        # logger.debug('Validating configuration value')
        self.assertTrue(found)

        os.remove(_conf_file)
