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

from playwright.sync_api import sync_playwright

from taf.foundation.api.ui.web import Browser as IBrowser


class Browser(IBrowser):
    _playwright = None
    _browser_instance = None

    def __init__(
            self,
            name='chromium',
            identifier=None,
            **kwargs
    ):
        self._headless = kwargs.pop('headless', True)
        self._browser_type = name

        super().__init__(
            name, identifier, **kwargs
        )

    @staticmethod
    def launch(url='about:blank', **kwargs):  # type: ignore[override]
        if not Browser.cache:
            Browser(
                kwargs.get('name', 'chromium'),
                kwargs.get('identifier'),
                headless=kwargs.get('headless', True)
            )

        Browser.cache.current.goto(url)  # type: ignore[union-attr]

    def activate(self):
        super().activate()

    def maximize(self):
        pass

    def sync(self, timeout=30):
        if self.cache and self.cache.current:
            self.cache.current.wait_for_load_state(
                'networkidle',
                timeout=timeout * 1000
            )

    def get_screenshot_data(self):
        if self.cache and self.cache.current:
            return self.cache.current.screenshot()
        raise RuntimeError('No active page')

    def close(self):
        super().close()

        if not self.cache:
            if Browser._browser_instance:
                Browser._browser_instance.close()
                Browser._browser_instance = None
            if Browser._playwright:
                Browser._playwright.stop()
                Browser._playwright = None

    def _create_instance(self, name, **kwargs):
        if not Browser._playwright:
            Browser._playwright = sync_playwright().start()

        browser_types = {
            'chromium': Browser._playwright.chromium,
            'chrome': Browser._playwright.chromium,
            'firefox': Browser._playwright.firefox,
            'webkit': Browser._playwright.webkit,
        }

        launcher = browser_types.get(
            name.lower() if name else 'chromium'
        )
        if not launcher:
            raise ValueError(
                'Unsupported browser: {}'.format(name)
            )

        if not Browser._browser_instance:
            Browser._browser_instance = launcher.launch(
                headless=self._headless,
                channel='chrome' if (name and name.lower() == 'chrome') else None,
            )

        return Browser._browser_instance.new_page()
