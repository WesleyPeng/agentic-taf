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


class BasePlugin(type):
    plugin_path = os.path.join(
        os.path.dirname(__file__),
        'plugins'
    )

    def __init__(cls, name, bases, attributes):
        if not hasattr(cls, 'plugins'):
            cls.plugins = {}
        else:
            identifier = name.lower()
            cls.plugins[identifier] = cls

        super().__init__(
            name, bases, attributes
        )

    @staticmethod
    def register_plugin_dir(plugin_path):
        assert os.path.isdir(plugin_path)

        BasePlugin.plugin_path = plugin_path
