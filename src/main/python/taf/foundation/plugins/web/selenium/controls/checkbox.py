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

from taf.foundation.api.ui.controls import CheckBox as ICheckBox
from taf.foundation.plugins.web.selenium.webelement import WebElement


class CheckBox(WebElement, ICheckBox):
    def tick(self):
        if not self.state:
            self.toggle()

    def untick(self):
        if self.state:
            self.toggle()

    def toggle(self):
        self.current.click()

    @property
    def state(self):
        assert self.exists() and self.object.is_enabled(), \
            'N/A - invisible/disabled element'

        _checked = self.object.get_attribute('checked')

        return _checked and ('false' != _checked)
