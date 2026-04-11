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

from taf.foundation.api.ui.web import Page


class BasePage(Page):
    def __init__(self, url=None, *elements, **conditions):
        super().__init__(
            *elements, **conditions
        )

        if url:
            self.parent.launch(url)
            self.parent.maximize()

        self.parent.sync()
