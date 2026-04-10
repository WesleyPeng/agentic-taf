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

from taf.foundation.utils import YAMLData


class Configuration(object):
    _instance = None
    _settings = None

    def __init__(self):
        if not Configuration._instance:
            Configuration._settings = YAMLData.load(
                os.path.join(
                    os.path.dirname(__file__),
                    'config.yml'
                )
            )

            Configuration._instance = self

    @classmethod
    def get_instance(cls):
        if not Configuration._instance:
            Configuration()

        return Configuration._instance

    @property
    def plugins(self):
        return self._settings.plugins

    def save_as(self, path):
        self.plugins.dump(path)
