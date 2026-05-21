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

"""Template Method base for Selenium-backed wait handlers.

BrowserWaitHandler and ElementWaitHandler had nearly identical
constructors + WebDriverWait boilerplate, varying only in the JS
predicate and the timeout message. This base factors out the shared
shape so each subclass declares just the per-script bits.
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from taf.foundation.api.ui.support import WaitHandler


class SeleniumWaitHandler(WaitHandler):
    """Shared base for Selenium ``wait()`` implementations.

    Subclasses implement ``wait(timeout)`` and call :meth:`_wait_for_script`
    with the predicate JS + a format-string failure message (``{timeout}``
    placeholder for the elapsed-seconds value).
    """

    def __init__(self, handler=None, timeout=None, poll_frequency=1.0):
        super().__init__(handler, timeout)
        self.poll_frequency = poll_frequency or 1.0

    def _wait_for_script(
        self,
        script: str,
        timeout_message: str,
        timeout: float | None = None,
    ) -> None:
        """Wait until ``script`` (a JS expression returning truthy) succeeds.

        Args:
            script: JS to execute on each poll. Must return truthy when
                the wait should end.
            timeout_message: Format string with a ``{timeout}`` placeholder
                for the elapsed-seconds value, used in the TimeoutException
                message if the predicate never becomes true.
            timeout: Override the instance's ``self.timeout``.
        """
        try:
            self.timeout = float(timeout or self.timeout)
            self.poll_frequency = float(self.poll_frequency)
            WebDriverWait(
                self.handler,
                self.timeout,
                self.poll_frequency,
            ).until(
                lambda driver: driver.execute_script(script),
                timeout_message.format(timeout=self.timeout),
            )
        except TimeoutException:
            raise
