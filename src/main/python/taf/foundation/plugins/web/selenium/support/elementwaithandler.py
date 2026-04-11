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


class ElementWaitHandler(WaitHandler):
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
        Waits until the asynchronous animation complete
        :param timeout: float in seconds
        :return:
        """
        self.timeout = float(timeout or self.timeout)
        self.poll_frequency = float(self.poll_frequency)

        xmlhttp_animation_script = \
            'return (window.xmlhttp.readyState==4 && ' \
            'window.xmlhttp.status==200);'
        jquery_animation_script = 'return window.jQuery.active==0;'
        ajax_animation_script = 'return window.Ajax.activeRequestCount==0;'
        dojo_animation_script = \
            'return window.dojo.io.XMLHTTPTransport.inFlight.length==0;'
        angular_animation_script = \
            'return window.angular.element(document.body)' \
            '.injector().get("$http").pendingRequests.length==0;'

        animation_type_script_pairs = {
            'xmlhttp': xmlhttp_animation_script,
            'jQuery': jquery_animation_script,
            'Ajax': ajax_animation_script,
            'dojo': dojo_animation_script,
            'angular': angular_animation_script
        }

        for animation, script in animation_type_script_pairs.items():
            ret = self.handler.execute_script(
                'if (window.{}) return true; else return false;'.format(
                    animation
                )
            )

            ret = ret and ret != 'false'

            if ret:
                try:
                    WebDriverWait(
                        self.handler,
                        self.timeout,
                        self.poll_frequency
                    ).until(
                        lambda driver: driver.execute_script(script),
                        'Failed to wait for loading '
                        '{} element in {} seconds'.format(
                            animation,
                            self.timeout
                        )
                    )
                except TimeoutException:
                    raise
