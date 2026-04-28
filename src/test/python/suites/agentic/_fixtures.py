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

"""Test-suite-private helpers for plugin configuration overrides.

The Agentic QA platform suites need to swap which concrete plugin
ServiceLocator returns for a given plugin interface at fixture time
(e.g. ``HttpxRESTPlugin`` vs the default REST plugin, or enabling
the optional LLM judge). Each switch requires invalidating two
singleton caches before re-resolving:

* ``taf.foundation.conf.configuration.Configuration._instance``
  and ``._settings`` — the YAML config singleton.
* ``taf.foundation.servicelocator.ServiceLocator._plugins`` and
  ``._clients`` — per-plugin discovery caches.

Without the cache reset the new env-var override is ignored and the
tests resolve a stale client class. The pattern was duplicated for
each plugin in ``conftest.py``; this module pulls it into a single
:class:`ConfigurationFixture` helper.
"""

import os
from typing import Any, Type

from taf.foundation import ServiceLocator
from taf.foundation.conf.configuration import Configuration


class ConfigurationFixture:
    """Centralized helper for plugin-override fixtures.

    Encapsulates the env-set, singleton-reset, ServiceLocator-resolve,
    type-validate sequence that used to be hand-written per plugin.
    """

    @staticmethod
    def set_env(overrides: dict[str, str]) -> None:
        """Apply a batch of environment variable overrides.

        The keys are typically TAF_PLUGIN_<NAME>_<FIELD> for plugin
        configuration; values are forwarded to ``os.environ``.
        """
        for key, value in overrides.items():
            os.environ[key] = value

    @staticmethod
    def reset_singletons(plugin_interface: Type[Any]) -> None:
        """Invalidate Configuration + ServiceLocator caches for one plugin.

        We pop only the cache entries for the specific plugin interface
        so that other plugins resolved earlier in the session keep
        their cached client classes.
        """
        Configuration._instance = None
        Configuration._settings = None
        ServiceLocator._plugins.pop(plugin_interface, None)
        ServiceLocator._clients.pop(plugin_interface, None)

    @classmethod
    def resolve(
        cls,
        plugin_interface: Type[Any],
        expected_client_cls: Type[Any],
        env_overrides: dict[str, str] | None = None,
    ) -> Type[Any]:
        """Apply env overrides, reset singletons, and resolve the plugin.

        Args:
            plugin_interface: The plugin interface (e.g. ``RESTPlugin``).
            expected_client_cls: The concrete client class the test
                expects ServiceLocator to resolve to.
            env_overrides: Optional environment variable overrides
                applied before resetting the singletons.

        Returns:
            The resolved client class.

        Raises:
            AssertionError: If ServiceLocator returns ``None`` or a
                client class other than ``expected_client_cls``.
        """
        if env_overrides:
            cls.set_env(env_overrides)
        cls.reset_singletons(plugin_interface)

        client_cls = ServiceLocator.get_client(plugin_interface)
        assert client_cls is not None, (
            f'ServiceLocator failed to resolve {plugin_interface.__name__}'
        )
        assert client_cls is expected_client_cls, (
            f'Expected {expected_client_cls.__name__}, '
            f'got {client_cls.__name__}. '
            f'ServiceLocator did not resolve to the expected plugin.'
        )
        return client_cls
