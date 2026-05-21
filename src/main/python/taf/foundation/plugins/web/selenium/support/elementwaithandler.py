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


# Per-framework animation-complete predicates. Keys are the `window.<name>`
# globals to feature-detect; values are the JS expressions whose truthy
# return means the framework's in-flight async work is done.
_ANIMATION_SCRIPTS: dict[str, str] = {
    'xmlhttp': 'return (window.xmlhttp.readyState==4 && '
               'window.xmlhttp.status==200);',
    'jQuery': 'return window.jQuery.active==0;',
    'Ajax': 'return window.Ajax.activeRequestCount==0;',
    'dojo': 'return window.dojo.io.XMLHTTPTransport.inFlight.length==0;',
    'angular': 'return window.angular.element(document.body)'
               '.injector().get("$http").pendingRequests.length==0;',
}


class ElementWaitHandler(SeleniumWaitHandler):
    """Waits until in-flight async animations complete across known
    JS frameworks (xmlhttp, jQuery, Ajax, dojo, angular)."""

    def wait(self, timeout=None):
        self.timeout = float(timeout or self.timeout)
        self.poll_frequency = float(self.poll_frequency)
        for animation, script in _ANIMATION_SCRIPTS.items():
            present = self.handler.execute_script(
                'if (window.{}) return true; else return false;'.format(animation)
            )
            if not (present and present != 'false'):
                continue
            self._wait_for_script(
                script,
                'Failed to wait for loading {} element in {{timeout}} seconds'.format(animation),
                self.timeout,
            )
