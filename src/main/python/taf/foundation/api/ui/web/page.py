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
from .browser import Browser


class Page(UIElement):
    def __init__(self, *elements, **conditions):
        super().__init__(
            *elements, **conditions
        )

    @property
    def current(self):
        if self.parent and self.root:
            self._current = self

        return self._current

    def _resolve_parent(self, element=None):
        if element is None:
            if Browser.current:
                self._parent = Browser.current
            else:
                raise RuntimeError('Browser is required')
        else:
            if isinstance(element, Browser):
                self._parent = element
            else:
                raise TypeError(
                    'Invalid argument - parent'
                )

    def _resolve_root(self):
        if Browser.cache:
            self._root = Browser.cache.current
        else:
            raise RuntimeError(
                'UIAutomation Driver is required'
            )
