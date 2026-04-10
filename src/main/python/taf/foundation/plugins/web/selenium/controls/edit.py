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
from taf.foundation.plugins.web.selenium.webelement import WebElement


class Edit(WebElement, IEdit):
    def get_selection(self):
        raise RuntimeError(
            'Unsupported feature for web element'
        )

    @property
    def text(self):
        if self.exists():
            return self.object.text

        return r''

    @property
    def supports_text_selection(self):
        return True

    def set(self, value):
        assert not self.is_read_only, \
            'N/A - read-only element'

        self.object.clear()
        self.object.send_keys(value)

    @property
    def value(self):
        if self.exists():
            return self.object.get_attribute('value')

        return r''

    @property
    def is_read_only(self):
        assert self.exists(), 'N/A - invisible element'

        return not self.object.is_enabled()
