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

from taf.foundation.api.ui.web import WebElement as IWebElement
from taf.foundation.plugins.web.playwright.support.locator import Locator


class WebElement(IWebElement):
    def __init__(self, *elements, **conditions):
        super().__init__(*elements, **conditions)

    @property
    def locator_enum(self):
        return Locator

    @property
    def element_finder(self):
        from taf.foundation.plugins.web.playwright.support.elementfinder \
            import ElementFinder
        return ElementFinder

    def exists(self, timeout=30):
        try:
            el = self.current
            if el:
                return el.is_visible(timeout=timeout * 1000)
        except Exception:
            pass
        return False

    def activate(self):
        if self.object:
            self.object.focus()

    def highlight(self):
        if self.object:
            self.object.evaluate(
                'el => el.style.border = "2px solid yellow"'
            )

    def _resolve_anchor(self):
        anchor = super()._resolve_anchor()
        try:
            if anchor and hasattr(anchor, 'frame_locator'):
                tag = getattr(anchor, 'tag_name', None)
                if tag in ('iframe', 'frame'):
                    return self.root.cache.current
        except Exception:
            pass
        return anchor or (
            self.root.cache.current if self.root and self.root.cache else None
        )

    def _wrap_element(self, element):
        self._current = element
