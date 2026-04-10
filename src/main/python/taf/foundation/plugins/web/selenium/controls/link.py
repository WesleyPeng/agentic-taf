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

from taf.foundation.api.ui.controls import Link as ILink
from taf.foundation.plugins.web.selenium.webelement import WebElement


class Link(WebElement, ILink):
    @property
    def enabled(self):
        if self.exists():
            return self.object.is_enabled()

        return False

    def click(self):
        assert self.enabled, 'NA - disabled element'

        self.object.click()

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
