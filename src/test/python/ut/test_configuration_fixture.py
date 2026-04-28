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

"""Unit tests for ConfigurationFixture.

Locks the singleton-reset semantics that the platform suites rely on
when swapping plugins at fixture time.
"""

import os
import sys
from pathlib import Path

import pytest

# The fixture lives alongside the agentic suite's conftest. The suite
# directory isn't on sys.path by default for unit tests, so we add it.
_SUITE_DIR = Path(__file__).parent.parent / 'suites' / 'agentic'
if str(_SUITE_DIR) not in sys.path:
    sys.path.insert(0, str(_SUITE_DIR))

from _fixtures import ConfigurationFixture  # noqa: E402

from taf.foundation import ServiceLocator  # noqa: E402
from taf.foundation.api.plugins import RESTPlugin  # noqa: E402
from taf.foundation.conf.configuration import Configuration  # noqa: E402


class _FakePlugin:
    """Marker class used as a plugin interface in tests."""


class TestSetEnv:

    def test_set_env_writes_to_os_environ(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv('TAF_TEST_KEY_1', raising=False)
        monkeypatch.delenv('TAF_TEST_KEY_2', raising=False)

        ConfigurationFixture.set_env({
            'TAF_TEST_KEY_1': 'value-1',
            'TAF_TEST_KEY_2': 'value-2',
        })
        assert os.environ['TAF_TEST_KEY_1'] == 'value-1'
        assert os.environ['TAF_TEST_KEY_2'] == 'value-2'

    def test_empty_dict_is_noop(self) -> None:
        # Should not raise, should not mutate os.environ
        before = dict(os.environ)
        ConfigurationFixture.set_env({})
        assert dict(os.environ) == before


class TestResetSingletons:

    def test_clears_configuration_singleton(self) -> None:
        # Force-prime the Configuration singleton.
        Configuration._instance = object()  # type: ignore[assignment]
        Configuration._settings = {'sentinel': True}  # type: ignore[assignment]

        ConfigurationFixture.reset_singletons(_FakePlugin)
        assert Configuration._instance is None
        assert Configuration._settings is None

    def test_pops_only_target_plugin_caches(self) -> None:
        # Stash sentinel entries for two plugin interfaces.
        ServiceLocator._plugins[_FakePlugin] = 'fake-plugin'
        ServiceLocator._clients[_FakePlugin] = 'fake-client'
        ServiceLocator._plugins[RESTPlugin] = 'rest-plugin-sentinel'
        ServiceLocator._clients[RESTPlugin] = 'rest-client-sentinel'

        ConfigurationFixture.reset_singletons(_FakePlugin)

        # Target plugin caches were popped.
        assert _FakePlugin not in ServiceLocator._plugins
        assert _FakePlugin not in ServiceLocator._clients

        # Other plugin caches are preserved.
        assert ServiceLocator._plugins.get(RESTPlugin) == 'rest-plugin-sentinel'
        assert ServiceLocator._clients.get(RESTPlugin) == 'rest-client-sentinel'

        # Cleanup
        ServiceLocator._plugins.pop(RESTPlugin, None)
        ServiceLocator._clients.pop(RESTPlugin, None)

    def test_no_op_if_target_not_in_caches(self) -> None:
        # Should not raise even when nothing to pop.
        ServiceLocator._plugins.pop(_FakePlugin, None)
        ServiceLocator._clients.pop(_FakePlugin, None)
        ConfigurationFixture.reset_singletons(_FakePlugin)


class TestResolve:

    def test_raises_when_service_locator_returns_none(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            ServiceLocator, 'get_client', lambda iface: None,
        )

        with pytest.raises(AssertionError, match='failed to resolve'):
            ConfigurationFixture.resolve(
                plugin_interface=_FakePlugin,
                expected_client_cls=str,
            )

    def test_raises_on_unexpected_client_class(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class _ExpectedCls:
            pass

        class _ActualCls:
            pass

        monkeypatch.setattr(
            ServiceLocator, 'get_client', lambda iface: _ActualCls,
        )

        with pytest.raises(AssertionError, match='did not resolve to the expected plugin'):
            ConfigurationFixture.resolve(
                plugin_interface=_FakePlugin,
                expected_client_cls=_ExpectedCls,
            )

    def test_returns_client_cls_on_success(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class _ExpectedCls:
            pass

        monkeypatch.setattr(
            ServiceLocator, 'get_client', lambda iface: _ExpectedCls,
        )

        result = ConfigurationFixture.resolve(
            plugin_interface=_FakePlugin,
            expected_client_cls=_ExpectedCls,
        )
        assert result is _ExpectedCls

    def test_applies_env_overrides_before_resolving(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen_env: dict[str, str] = {}

        def fake_get_client(_iface: object) -> type:
            # Capture the env state ServiceLocator would see at this point
            seen_env['TAF_PROBE'] = os.environ.get('TAF_PROBE', '')
            return str

        monkeypatch.setattr(ServiceLocator, 'get_client', fake_get_client)
        monkeypatch.delenv('TAF_PROBE', raising=False)

        ConfigurationFixture.resolve(
            plugin_interface=_FakePlugin,
            expected_client_cls=str,
            env_overrides={'TAF_PROBE': 'set-by-fixture'},
        )

        # The override was visible to ServiceLocator at resolution time
        assert seen_env['TAF_PROBE'] == 'set-by-fixture'

    def test_resets_caches_on_each_call(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Pre-populate the cache; resolve should clear it.
        ServiceLocator._plugins[_FakePlugin] = 'stale'
        ServiceLocator._clients[_FakePlugin] = 'stale'

        called: list[bool] = []

        def fake_get_client(iface: type) -> type:
            # By the time get_client runs, the cache should already be
            # cleared by reset_singletons().
            called.append(True)
            assert iface not in ServiceLocator._plugins
            assert iface not in ServiceLocator._clients
            return str

        monkeypatch.setattr(ServiceLocator, 'get_client', fake_get_client)

        ConfigurationFixture.resolve(
            plugin_interface=_FakePlugin,
            expected_client_cls=str,
        )
        assert called == [True]
