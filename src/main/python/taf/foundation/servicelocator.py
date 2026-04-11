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

import glob
import importlib.util
import inspect
import os

from taf.foundation.api.plugins import CLIPlugin
from taf.foundation.api.plugins import WebPlugin
from taf.foundation.api.ui import AUT
from taf.foundation.api.ui import UIElement
from taf.foundation.conf import Configuration


class ServiceLocator:
    _plugins: dict[type, type] = {}
    _clients: dict[type, object] = {}

    def __init__(self, plugin_type: type = WebPlugin) -> None:
        if plugin_type not in ServiceLocator._plugins:
            self._identify_plugin_by_type(
                plugin_type
            )

    @classmethod
    def get_app_under_test(
            cls,
            plugin=WebPlugin
    ):
        _instance = cls._get_plugin_instance_by_type(
            plugin
        )
        assert hasattr(
            _instance, 'app_under_test'
        ) and issubclass(
            _instance.app_under_test, AUT
        )

        return _instance.app_under_test

    @classmethod
    def get_modeled_control(
            cls,
            control_type,
            plugin=WebPlugin
    ):
        _instance = cls._get_plugin_instance_by_type(
            plugin
        )
        assert hasattr(_instance, 'controls')

        for control in _instance.controls:
            if issubclass(control, control_type):
                break
        else:
            control = type(
                control_type.__name__,
                (UIElement,),
                {}
            )

        return control

    @classmethod
    def get_client(
            cls,
            plugin=CLIPlugin
    ):
        if plugin not in cls._clients:
            _instance = cls._get_plugin_instance_by_type(
                plugin
            )

            assert hasattr(_instance, 'client')

            ServiceLocator._clients[plugin] = _instance.client

        return cls._clients.get(plugin)

    def _identify_plugin_by_type(self, plugin_type: type) -> None:
        _base_dir = os.path.join(
            os.path.dirname(__file__),
            'conf'
        )

        for _, plugin in vars(
                Configuration.get_instance().plugins
        ).items():
            if plugin.enabled:
                for cls in self._inspect_classes(
                        os.path.abspath(
                            os.path.join(
                                _base_dir,
                                plugin.location
                            )
                        )
                ):
                    if issubclass(
                            cls, plugin_type
                    ) and cls is not plugin_type:
                        ServiceLocator._plugins[plugin_type] = cls
                        break

                if plugin_type in self._plugins:
                    break

    def _inspect_classes(self, plugin_dir: str) -> list[type]:
        classes: list[type] = []

        try:
            for py in self._find_python_files(plugin_dir):
                classes.extend(
                    cls for cls in self._import_classes(py)
                )
        except Exception:
            raise

        return classes

    def _find_python_files(self, directory: str) -> list[str]:
        _cd = os.path.realpath(directory)

        files = [
            os.path.abspath(_file)
            for _file in glob.iglob(
                os.path.join(_cd, '*.py'))
        ]

        for _chdir in os.listdir(_cd):
            if os.path.isdir(
                    os.path.join(_cd, _chdir)
            ):
                files.extend(
                    self._find_python_files(
                        os.path.join(_cd, _chdir)
                    )
                )

        return files

    def _import_classes(self, location: str) -> list[type]:
        classes: list[type] = []

        try:
            path, filename = os.path.split(location)
            module_name = os.path.splitext(filename)[0]

            spec = importlib.util.spec_from_file_location(
                module_name, location
            )
            if spec is None or spec.loader is None:
                return classes

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            classes.extend(
                cls for _, cls in inspect.getmembers(
                    module,
                    predicate=inspect.isclass
                )
            )
        except ImportError:
            # Optional plugin dependency not installed — skip this module
            pass
        except OSError:
            pass

        return classes

    @classmethod
    def _get_plugin_instance_by_type(cls, plugin_type):
        if plugin_type not in ServiceLocator._plugins:
            ServiceLocator(plugin_type)

        cls_plugin = cls._plugins.get(
            plugin_type, None
        )

        if cls_plugin is None:
            raise TypeError(
                'Unable to load {} plugin'.format(
                    plugin_type
                )
            )

        return cls_plugin()
