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
