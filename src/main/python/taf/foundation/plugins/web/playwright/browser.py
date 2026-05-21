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
