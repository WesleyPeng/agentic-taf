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

from selenium import webdriver
from selenium.webdriver import Remote as RemoteWebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from taf.foundation.api.ui.web import Browser as IBrowser
from taf.foundation.plugins.web.selenium.support.browserwaithandler import \
    BrowserWaitHandler


class Browser(IBrowser):
    def __init__(
            self,
            name='firefox',
            identifier=None,
            **kwargs
    ):
        super().__init__(
            name, identifier, **kwargs
        )

    @staticmethod
    def launch(url='about:blank', **kwargs):  # type: ignore[override]
        if not Browser.cache:
            Browser(
                kwargs.get('name'),
                kwargs.get('identifier')
            )

        Browser.cache.current.get(url)  # type: ignore[union-attr]

        BrowserWaitHandler(
            Browser.cache.current,  # type: ignore[union-attr]
            kwargs.get('timeout', 30.0)
        ).wait()

    def activate(self):
        super().activate()

        self.cache.current.switch_to.window(  # type: ignore[union-attr]
            self.cache.current.current_window_handle  # type: ignore[union-attr]
        )

    def maximize(self):
        self.cache.current.maximize_window()  # type: ignore[union-attr]

    def sync(self, timeout=30):
        BrowserWaitHandler(
            self.cache.current,  # type: ignore[union-attr]
            timeout
        ).wait()

    def get_screenshot_data(self):
        if isinstance(self.cache.current, RemoteWebDriver):  # type: ignore[union-attr]
            return self.cache.current.get_screenshot_as_png()  # type: ignore[union-attr]
        else:
            raise RuntimeError(
                "Selenium Web Driver is required"
            )

    def _create_instance(
            self, name, **kwargs
    ):
        kwargs.setdefault('is_remote', False)

        is_remote = str(
            kwargs.pop('is_remote')
        ).lower() not in ('false', 'no')

        if is_remote:
            _browser_name = {
                'firefox': 'firefox', 'ff': 'firefox',
                'chrome': 'chrome', 'gc': 'chrome',
                'googlechrome': 'chrome',
            }.get(name.lower(), 'firefox')

            options = kwargs.get('options')
            if options is None:
                if _browser_name == 'chrome':
                    options = ChromeOptions()
                else:
                    options = FirefoxOptions()

            _instance = RemoteWebDriver(
                command_executor=kwargs.get(
                    'command_executor',
                    'http://{host}:{port}/wd/hub'.format(
                        host=kwargs.get('host', 'localhost'),
                        port=kwargs.get('port', 4444)
                    )
                ),
                options=options,
            )
        else:
            _browser_creation_strategies = {
                'ff': self._make_firefox,
                'firefox': self._make_firefox,
                'googlechrome': self._make_chrome,
                'chrome': self._make_chrome,
                'gc': self._make_chrome,
            }

            _creator = _browser_creation_strategies.get(
                name.lower()
            )

            if not callable(_creator):
                raise ValueError('Unsupported browser type')

            _instance = _creator(**kwargs)
            # _instance.get('about:blank')

        return _instance

    def _make_firefox(self, **kwargs):
        options = kwargs.pop('options', None)
        if options is None:
            options = FirefoxOptions()

        if kwargs.pop('headless', False):
            options.add_argument('--headless')

        service_kwargs = {}
        executable_path = kwargs.pop('executable_path', None)
        if executable_path:
            service_kwargs['executable_path'] = executable_path
        service = kwargs.pop('service', FirefoxService(**service_kwargs))

        return webdriver.Firefox(
            service=service,
            options=options,
            **kwargs
        )

    def _make_chrome(self, **kwargs):
        options = kwargs.pop('options', None)
        if options is None:
            options = ChromeOptions()

        if kwargs.pop('headless', False):
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        service_kwargs = {}
        executable_path = kwargs.pop('executable_path', None)
        if executable_path:
            service_kwargs['executable_path'] = executable_path
        service = kwargs.pop('service', ChromeService(**service_kwargs))

        return webdriver.Chrome(
            service=service,
            options=options,
            **kwargs
        )
