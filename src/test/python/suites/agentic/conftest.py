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

"""Shared fixtures for Agentic QA Platform E2E test suites.

Uses ServiceLocator with config override to resolve HttpClient
from the httpx plugin — proves the full discovery chain works:
  config.yml + env override → ServiceLocator → HttpxRESTPlugin → HttpClient
"""

import os

import pytest
import yaml

from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import RESTPlugin
from taf.foundation.conf.configuration import Configuration


_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')


def _load_config():
    env = os.environ.get('TAF_ENV', 'preprod')
    config_path = os.path.join(_CONFIG_DIR, f'{env}.yml')
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    if os.environ.get('AGENT_BASE_URL'):
        cfg['agent']['base_url'] = os.environ['AGENT_BASE_URL']

    return cfg


def _configure_httpx_plugin():
    """Switch REST plugin to httpx via env overrides, then resolve via ServiceLocator."""
    os.environ['TAF_PLUGIN_REST_NAME'] = 'HttpxRESTPlugin'
    os.environ['TAF_PLUGIN_REST_LOCATION'] = '../plugins/svc/httpx'

    # Reset singletons so config reload picks up the override
    Configuration._instance = None
    Configuration._settings = None
    ServiceLocator._plugins.pop(RESTPlugin, None)
    ServiceLocator._clients.pop(RESTPlugin, None)

    # Resolve through ServiceLocator — this proves the chain:
    # config.yml + env override → ServiceLocator → HttpxRESTPlugin → HttpClient
    client_cls = ServiceLocator.get_client(RESTPlugin)
    assert client_cls is not None, 'ServiceLocator failed to resolve REST plugin'

    from taf.foundation.plugins.svc.httpx import HttpClient
    assert client_cls is HttpClient, (
        f'Expected HttpClient, got {client_cls}. '
        'ServiceLocator did not resolve to httpx plugin.'
    )

    return client_cls


@pytest.fixture(scope='session')
def config():
    return _load_config()


@pytest.fixture(scope='session')
def agent_url(config):
    return config['agent']['base_url']


@pytest.fixture(scope='session')
def auth_headers(config):
    """Default auth headers for API requests."""
    return {
        'X-User': config['auth']['default_user'],
        'X-Team': config['auth']['default_team'],
        'X-Role': config['auth']['roles']['developer'],
    }


@pytest.fixture(scope='session')
def rest_client_cls():
    """Resolve HttpClient via ServiceLocator with config override.

    This validates that the ServiceLocator correctly discovers
    HttpxRESTPlugin and returns HttpClient as the client class.
    """
    return _configure_httpx_plugin()


@pytest.fixture(scope='session')
def api_client(rest_client_cls, agent_url, auth_headers):
    """Session-scoped REST client resolved via ServiceLocator.

    Instantiates the client class discovered by ServiceLocator
    (HttpClient from httpx plugin) with the agent URL and auth headers.
    """
    with rest_client_cls(
        agent_url,
        headers=auth_headers,
        timeout=30,
    ) as client:
        yield client


def auth_headers_for_role(config, role):
    """Build auth headers for a specific role."""
    return {
        'X-User': config['auth']['default_user'],
        'X-Team': config['auth']['default_team'],
        'X-Role': config['auth']['roles'].get(role, role),
    }
