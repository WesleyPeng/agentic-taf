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
