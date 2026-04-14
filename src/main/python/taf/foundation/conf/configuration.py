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
from typing import Any

from taf.foundation.utils import YAMLData


class Configuration:
    _instance: 'Configuration | None' = None
    _settings: YAMLData | None = None

    def __init__(self) -> None:
        if not Configuration._instance:
            Configuration._settings = YAMLData.load(
                os.path.join(
                    os.path.dirname(__file__),
                    'config.yml'
                )
            )

            self._apply_env_overrides()
            Configuration._instance = self

    @classmethod
    def get_instance(cls) -> 'Configuration':
        if not Configuration._instance:
            Configuration()

        assert Configuration._instance is not None
        return Configuration._instance

    @property
    def plugins(self) -> Any:
        assert self._settings is not None
        return self._settings.plugins

    def save_as(self, path: str) -> None:
        self.plugins.dump(path)

    def _apply_env_overrides(self) -> None:
        """Override plugin config from TAF_PLUGIN_<NAME>_<KEY> env vars.

        Example: TAF_PLUGIN_WEB_ENABLED=false disables the web plugin.
        """
        if self._settings is None:
            return

        prefix = 'TAF_PLUGIN_'
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            parts = key[len(prefix):].lower().split('_', 1)
            if len(parts) != 2:
                continue

            plugin_name, attr_name = parts
            if hasattr(self._settings, 'plugins'):
                plugins = vars(self._settings.plugins)
                # Case-insensitive lookup — config keys may be mixed case (e.g., 'REST')
                matched_key = None
                for k in plugins:
                    if k.lower() == plugin_name:
                        matched_key = k
                        break
                if matched_key:
                    plugin_conf = plugins[matched_key]
                    parsed_value: str | bool = value
                    if attr_name == 'enabled':
                        parsed_value = value.lower() in ('true', '1', 'yes')
                    setattr(plugin_conf, attr_name, parsed_value)
