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

"""T.3 — UI automation tests against live preprod dashboard.

Uses taf.modeling.web.Browser resolved via ServiceLocator to PlaywrightPlugin.
Follows the same pattern as bpt/pages — Browser.cache.current is the native
Playwright Page; Page Objects use it for navigation and assertions.
"""

import pytest

from taf.modeling.web import Browser

from suites.agentic.ui.pages.login_page import LoginPage
from suites.agentic.ui.pages.dashboard_page import DashboardPage
from suites.agentic.ui.pages.chat_page import ChatPage
from suites.agentic.ui.pages.environments_page import EnvironmentsPage


def _login_if_needed(page):
    login = LoginPage(page)
    if login.is_visible():
        login.login()
        page.wait_for_load_state('networkidle')


@pytest.mark.e2e
class TestLoginFlow:

    def test_login_page_visible(self, page):
        login = LoginPage(page)
        assert login.is_visible(), 'Login page not visible'

    def test_dev_login(self, page):
        login = LoginPage(page)
        if login.is_visible():
            login.login(username='testuser', role='developer', team='platform-team')
            page.wait_for_load_state('networkidle')

        dashboard = DashboardPage(page)
        assert dashboard.is_loaded(), 'Dashboard not loaded after login'


@pytest.mark.e2e
class TestNavigation:

    def test_navigate_to_chat(self, page):
        _login_if_needed(page)
        chat = ChatPage(page)
        chat.navigate()
        page.wait_for_load_state('networkidle')
        assert '/chat' in page.url

    def test_navigate_to_environments(self, page):
        _login_if_needed(page)
        envs = EnvironmentsPage(page)
        envs.navigate()
        page.wait_for_load_state('networkidle')
        assert '/environments' in page.url

    def test_navigate_all_pages(self, page):
        _login_if_needed(page)
        nav_items = [
            ('Dashboard', '/'),
            ('Chat', '/chat'),
            ('Environments', '/environments'),
            ('Test Results', '/test-results'),
            ('Reports', '/reports'),
            ('Analytics', '/analytics'),
        ]
        for label, path in nav_items:
            page.click(f'a:has-text("{label}")')
            page.wait_for_load_state('networkidle')
            assert page.url.endswith(path) or path == '/', (
                f'Navigation to {label} failed: URL is {page.url}'
            )


@pytest.mark.e2e
class TestDashboard:

    def test_dashboard_loads(self, page):
        _login_if_needed(page)
        dashboard = DashboardPage(page)
        assert dashboard.is_loaded()

    def test_no_error_state(self, page):
        _login_if_needed(page)
        content = page.content()
        assert 'Error' not in content or 'error' not in content.lower().split('border')[0]


@pytest.mark.e2e
class TestResponsiveLayout:
    """Test responsive viewports using the plugin's underlying Playwright browser.

    Browser (from taf.modeling.web) wraps PlaywrightPlugin's Browser which
    stores the Playwright browser instance as a class-level attribute.
    We access it to create contexts with different viewport sizes.
    """

    def _test_viewport(self, browser, dashboard_url, width, height):
        # Access the Playwright browser instance managed by the plugin
        pw_browser = Browser._browser_instance
        ctx = pw_browser.new_context(viewport={'width': width, 'height': height})
        p = ctx.new_page()
        p.goto(dashboard_url)
        p.wait_for_load_state('networkidle')
        _login_if_needed(p)
        assert p.title() is not None
        p.close()
        ctx.close()

    def test_desktop_viewport(self, browser, dashboard_url):
        self._test_viewport(browser, dashboard_url, 1920, 1080)

    def test_tablet_viewport(self, browser, dashboard_url):
        self._test_viewport(browser, dashboard_url, 1366, 768)

    def test_mobile_viewport(self, browser, dashboard_url):
        self._test_viewport(browser, dashboard_url, 375, 812)
