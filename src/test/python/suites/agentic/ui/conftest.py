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

"""Playwright fixtures for UI tests.

Follows the same pattern as bpt/pages — uses taf.modeling.web.Browser
(resolved via ServiceLocator to PlaywrightPlugin) and Page Objects
extend taf.foundation.api.ui.web.Page.

The config override to Playwright must happen before the modeling module
is imported, so it's done at conftest load time (before test collection).
"""

import os

# Config override MUST happen before taf.modeling.web is imported
# (Browser base class resolves at class-definition time)
os.environ['TAF_PLUGIN_WEB_NAME'] = 'PlaywrightPlugin'
os.environ['TAF_PLUGIN_WEB_LOCATION'] = '../plugins/web/playwright'

# Reset singletons so config reload picks up the override
from taf.foundation.conf.configuration import Configuration  # noqa: E402
from taf.foundation import ServiceLocator  # noqa: E402
from taf.foundation.api.plugins import WebPlugin  # noqa: E402

Configuration._instance = None
Configuration._settings = None
ServiceLocator._plugins.pop(WebPlugin, None)

import pytest  # noqa: E402

from taf.modeling.web import Browser  # noqa: E402


# Validate the chain resolved correctly
_browser_cls = ServiceLocator.get_app_under_test(WebPlugin)
from taf.foundation.plugins.web.playwright.browser import Browser as PwBrowser  # noqa: E402
assert _browser_cls is PwBrowser, (
    f'Expected PlaywrightPlugin Browser, got {_browser_cls}. '
    'ServiceLocator did not resolve to Playwright plugin.'
)


@pytest.fixture(scope='session')
def dashboard_url(config):
    return os.environ.get(
        'DASHBOARD_BASE_URL',
        config.get('dashboard', {}).get('base_url', 'http://localhost:18080'),
    )


@pytest.fixture(scope='session')
def browser(dashboard_url):
    """Session-scoped Browser from the framework's PlaywrightPlugin.

    Uses taf.modeling.web.Browser (same as bpt/bdd fixtures).
    The underlying Playwright Page is at Browser.cache.current.
    """
    b = Browser(name='chromium', headless=True)
    yield b
    b.close()


@pytest.fixture
def page(browser, dashboard_url):
    """Per-test Playwright Page from the plugin's Browser.

    Browser.cache.current is the native Playwright Page, same pattern
    as bpt/pages/basepage.py uses via self.parent / self.root.
    """
    pw_page = browser.cache.current
    pw_page.goto(dashboard_url)
    pw_page.wait_for_load_state('networkidle')
    yield pw_page
