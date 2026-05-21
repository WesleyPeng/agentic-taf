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
        super().__init__(
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
