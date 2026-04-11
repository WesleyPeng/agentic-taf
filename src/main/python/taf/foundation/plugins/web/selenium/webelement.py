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

from selenium.webdriver.remote.webelement import WebElement as SeElement

from taf.foundation.api.ui.web import WebElement as IWebElement
from taf.foundation.plugins.web.selenium.support.elementfinder import \
    ElementFinder
from taf.foundation.plugins.web.selenium.support.elementwaithandler import \
    ElementWaitHandler
from taf.foundation.plugins.web.selenium.support.locator import Locator


class WebElement(IWebElement):
    def __init__(
            self, *elements, **conditions
    ):
        super().__init__(
            *elements, **conditions
        )

    @property
    def locator_enum(self):
        return Locator

    @property
    def element_finder(self):
        return ElementFinder

    def exists(self, timeout=30):
        try:
            ElementWaitHandler(
                self.root.cache.current, timeout
            ).wait()
        except Exception:
            pass
        finally:
            try:
                _visible = self.current.is_displayed()
            except Exception:
                _visible = False

        return _visible

    def activate(self):
        if self.exists():
            self.root.cache.current.execute_script(
                'arguments[0].focus();',
                self.object
            )

    def highlight(self):
        self.activate()

        self.root.cache.current.execute_script(
            'arguments[0].setAttribute("style", arguments[1]);',
            self.object,
            'color: green; border: 2px solid yellow;'
        )

    def _resolve_anchor(self):
        anchor = super(
            WebElement, self
        )._resolve_anchor()

        try:
            if getattr(
                    anchor,
                    Locator.TAG.value,
                    None
            ) in ('iframe', 'frame'):
                anchor = self.root.cache.current
        except Exception:
            anchor = self.root.cache.current

        return anchor

    def _wrap_element(self, element):
        if isinstance(element, SeElement):
            self._current = element
        else:
            raise RuntimeError(
                'Non-supported element'
            )
