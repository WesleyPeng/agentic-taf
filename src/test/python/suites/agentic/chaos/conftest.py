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

    Configuration.reset()
    ServiceLocator.reset(ChaosPlugin)

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
