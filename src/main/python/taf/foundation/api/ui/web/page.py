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
