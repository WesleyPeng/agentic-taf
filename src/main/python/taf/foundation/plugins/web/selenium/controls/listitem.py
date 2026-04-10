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

from taf.foundation.api.ui.controls import ListItem as IListItem
from taf.foundation.plugins.web.selenium.webelement import WebElement


class ListItem(WebElement, IListItem):
    def select(self):
        if not self.is_selected:
            self.object.click()

    def deselect(self):
        if self.is_selected:
            self.object.click()

    @property
    def is_selected(self):
        assert self.exists(), 'N/A - item is not available'

        return self.object.is_selected()
