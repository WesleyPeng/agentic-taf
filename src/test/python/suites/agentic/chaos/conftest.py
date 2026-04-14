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

"""Chaos experiment fixtures — resolve K8sChaosPlugin via ServiceLocator."""

import importlib
import os

import pytest

from taf.foundation.api.plugins import ChaosPlugin
from taf.foundation.conf.configuration import Configuration
from taf.foundation import ServiceLocator

_has_kubernetes = importlib.util.find_spec('kubernetes') is not None


def _configure_chaos_plugin():
    """Enable chaos plugin via env override, resolve via ServiceLocator."""
    os.environ['TAF_PLUGIN_CHAOS_ENABLED'] = 'true'

    Configuration._instance = None
    Configuration._settings = None
    ServiceLocator._plugins.pop(ChaosPlugin, None)
    ServiceLocator._clients.pop(ChaosPlugin, None)

    client_cls = ServiceLocator.get_client(ChaosPlugin)
    assert client_cls is not None, 'ServiceLocator failed to resolve Chaos plugin'

    from taf.foundation.plugins.chaos.k8s.k8schaosclient import K8sChaosClient
    assert client_cls is K8sChaosClient, (
        f'Expected K8sChaosClient, got {client_cls}.'
    )
    return client_cls


@pytest.fixture(scope='session')
def chaos_client_cls():
    """Resolve K8sChaosClient via ServiceLocator."""
    if not _has_kubernetes:
        pytest.skip('kubernetes not installed')
    return _configure_chaos_plugin()


@pytest.fixture(scope='session')
def chaos_client(chaos_client_cls):
    """Session-scoped K8sChaosClient for the agentic-platform namespace.

    Kubeconfig resolution follows standard kubernetes SDK order:
      1. KUBECONFIG env var (if set)
      2. In-cluster config (if running inside K8s)
      3. ~/.kube/config (default)
    """
    kwargs = {'namespace': 'agentic-platform'}
    kubeconfig = os.environ.get('KUBECONFIG')
    if kubeconfig:
        kwargs['kubeconfig'] = kubeconfig
    return chaos_client_cls(**kwargs)
