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

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from taf.foundation.api.ui.support import WaitHandler


class BrowserWaitHandler(WaitHandler):
    def __init__(
            self,
            handler=None,
            timeout=None,
            poll_frequency=1.0
    ):
        super(BrowserWaitHandler, self).__init__(
            handler, timeout
        )

        self.poll_frequency = poll_frequency or 1.0

    def wait(self, timeout=None):
        """
        Waits until the page is fully loaded
        :param timeout: float in seconds
        :return:
        """
        try:
            self.timeout = float(timeout or self.timeout)
            self.poll_frequency = float(self.poll_frequency)

            WebDriverWait(
                self.handler,
                self.timeout,
                self.poll_frequency
            ).until(
                lambda driver: driver.execute_script(
                    'return document.readyState=="complete";'
                ),
                'Failed to fully load page in {} seconds'.format(
                    self.timeout
                )
            )
        except TimeoutException:
            raise
