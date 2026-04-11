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
