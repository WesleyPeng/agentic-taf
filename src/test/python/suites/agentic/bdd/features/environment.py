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

"""Behave environment — set up HttpClient via ServiceLocator for BDD scenarios."""

import os

from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import RESTPlugin
from taf.foundation.conf.configuration import Configuration


def before_all(context):
    """Configure HttpClient via ServiceLocator before any scenario runs."""
    os.environ['TAF_PLUGIN_REST_NAME'] = 'HttpxRESTPlugin'
    os.environ['TAF_PLUGIN_REST_LOCATION'] = '../plugins/svc/httpx'

    Configuration._instance = None
    Configuration._settings = None
    ServiceLocator._plugins.pop(RESTPlugin, None)
    ServiceLocator._clients.pop(RESTPlugin, None)

    client_cls = ServiceLocator.get_client(RESTPlugin)
    from taf.foundation.plugins.svc.httpx import HttpClient
    assert client_cls is HttpClient

    base_url = os.environ.get('AGENT_BASE_URL', 'http://localhost:18000')
    context.api_client = client_cls(
        base_url,
        headers={
            'X-User': 'bdd-testuser',
            'X-Team': 'test-team',
            'X-Role': 'developer',
        },
        timeout=30,
    )


def after_all(context):
    if hasattr(context, 'api_client') and context.api_client:
        context.api_client.__exit__(None, None, None)
