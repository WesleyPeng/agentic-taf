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

from taf.foundation.plugins.web.selenium.support._waitbase import SeleniumWaitHandler


class BrowserWaitHandler(SeleniumWaitHandler):
    """Waits until ``document.readyState === 'complete'``."""

    _SCRIPT = 'return document.readyState=="complete";'
    _TIMEOUT_MESSAGE = 'Failed to fully load page in {timeout} seconds'

    def wait(self, timeout=None):
        self._wait_for_script(self._SCRIPT, self._TIMEOUT_MESSAGE, timeout)
