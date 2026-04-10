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

from taf.foundation.api.ui.controls import Button as IButton
from taf.foundation.plugins.web.selenium.webelement import WebElement


class Button(WebElement, IButton):
    @property
    def enabled(self):
        if self.exists():
            return self.object.is_enabled()

        return False

    def click(self):
        assert self.enabled, 'NA - disabled element'

        self.object.click()
