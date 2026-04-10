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

import os
import sys

from selenium import webdriver
from selenium.webdriver import Remote as RemoteWebDriver

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
        super(Browser, self).__init__(
            name, identifier, **kwargs
        )

    @staticmethod
    def launch(url='about:blank', **kwargs):
        if not Browser.cache:
            Browser(
                kwargs.get('name'),
                kwargs.get('identifier')
            )

        Browser.cache.current.get(url)

        BrowserWaitHandler(
            Browser.cache.current,
            kwargs.get('timeout', 30.0)
        ).wait()

    def activate(self):
        super(Browser, self).activate()

        self.cache.current.switch_to.window(
            self.cache.current.current_window_handle
        )

    def maximize(self):
        self.cache.current.maximize_window()

    def sync(self, timeout=30):
        BrowserWaitHandler(
            self.cache.current,
            timeout
        ).wait()

    def get_screenshot_data(self):
        if isinstance(self.cache.current, RemoteWebDriver):
            return self.cache.current.get_screenshot_as_png()
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
            _instance = RemoteWebDriver(
                command_executor=kwargs.get(
                    'command_executor',
                    'http://{host}:{port}/wd/hub'.format(
                        host=kwargs.get('host', 'localhost'),
                        port=kwargs.get('port', 4444)
                    )
                ),
                desired_capabilities=kwargs.get(
                    'desired_capabilities',
                    {
                        'browserName': {
                            'firefox': 'firefox',
                            'ff': 'firefox',
                            'chrome': 'chrome',
                            'gc': 'chrome',
                            'googlechrome': 'chrome'
                        }.get(
                            name.lower(),
                            'firefox'
                        ),
                    }
                ),
                browser_profile=kwargs.get('browser_profile'),
                proxy=kwargs.get('proxy'),
                keep_alive=kwargs.get('keep_alive', False),
                file_detector=kwargs.get('file_detector'),
                options=kwargs.get('options')
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
        return webdriver.Firefox(**kwargs)

    def _make_chrome(self, **kwargs):
        _driver_dir = os.path.join(
            os.path.dirname(__file__),
            'support'
        )

        _default_driver_dir = os.path.join(
            _driver_dir,
            'chromedriver.exe'
        )

        if sys.platform.startswith('linux'):
            _default_driver_dir = \
                '/opt/google/chrome/chromedriver'

        if os.path.exists(_default_driver_dir):
            _driver_bin_file_path = _default_driver_dir
        else:
            _driver_bin_file_path = os.path.join(
                _driver_dir, 'chromedriver'
            )

        os.environ['webdriver.chrome.driver'] = \
            _driver_bin_file_path

        return webdriver.Chrome(
            _driver_bin_file_path,
            **kwargs
        )
