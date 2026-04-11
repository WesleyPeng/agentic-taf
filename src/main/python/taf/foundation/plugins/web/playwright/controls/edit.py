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

from taf.foundation.api.ui.controls import Edit as IEdit
from taf.foundation.plugins.web.playwright.webelement import WebElement


class Edit(WebElement, IEdit):
    @property
    def value(self):
        if self.object:
            return self.object.input_value()
        return ''

    def set(self, value):
        if self.object:
            self.object.fill(str(value))
