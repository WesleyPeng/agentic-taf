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

from taf.foundation.api.ui import UIElement
from taf.foundation.api.ui.support import ElementFinder
from taf.foundation.api.ui.support import Locator
from .browser import Browser
from .page import Page


class WebElement(UIElement):
    def __init__(self, *elements, **conditions):
        super(WebElement, self).__init__(
            *elements, **conditions
        )

    @property
    def locator_enum(self):
        return Locator

    @property
    def element_finder(self):
        return ElementFinder

    def _parse_conditions(self, **conditions):
        for key, value in conditions.items():
            try:
                key = self.locator_enum[key.upper()]
            except KeyError:
                self._constraints[key] = value
            else:
                self._locators[key] = value

    def _find_current_element(self):
        prioritized_locators = [
            (key, self._locators.get(key))
            for key in self.locator_enum.prioritized_locators()
            if key in self._locators
        ]

        return self.element_finder(
            anchor=self._resolve_anchor()
        ).find_element(
            *prioritized_locators,
            **self._constraints
        )

    def _resolve_anchor(self):
        if isinstance(self.parent, WebElement):
            anchor = self.parent.object
        elif isinstance(self.parent, Page):
            anchor = self.parent.root
        else:
            anchor = self.root.cache.current

        return anchor

    def _resolve_parent(self, element=None):
        if element is None:
            self._parent = Page(self)
        else:
            if isinstance(element, (WebElement, Page)):
                self._parent = element
            else:
                self._parent = self.create(element=element)

    def _resolve_root(self):
        if Browser.current:
            self._root = Browser.current
        else:
            raise RuntimeError('Browser is required')
