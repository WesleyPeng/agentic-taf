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

import warnings

from taf.foundation.api.ui.controls import Frame as IFrame
from taf.foundation.plugins.web.selenium.support.elementfinder import ElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator
from taf.foundation.plugins.web.selenium.webelement import WebElement


class Frame(WebElement, IFrame):
    def __init__(self, *elements, **conditions):
        conditions.setdefault('tag', 'iframe')

        WebElement.__init__(
            self, *elements, **conditions
        )

    def __enter__(self):
        if self.exists():
            self.root.cache.current.switch_to.frame(
                self.object
            )

        return self

    def __exit__(self, *args):
        self.root.cache.current.switch_to.parent_frame()

    def activate(self):
        warnings.warn(
            'Use context manager "with Frame(id=frame)" instead',
            DeprecationWarning
        )

        self.__enter__()

    def deactivate(self):
        warnings.warn(
            'Use context manager "with Frame(id=frame)" instead',
            DeprecationWarning
        )

        self.__exit__()

    @property
    def items(self):
        if not self._children:
            self._children = [  # type: ignore[assignment]
                WebElement.create(element=element, parent=self)
                for element in ElementFinder(
                    self.object
                ).find_elements(
                    Locator.XPATH, './/*'
                ) if element
            ]

        return (child for child in self._children)
