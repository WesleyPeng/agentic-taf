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

from taf.modeling.web import WebButton
from taf.modeling.web import WebTextBox
from .basepage import BasePage
from .searchresultspage import SearchResultsPage


class BingHomePage(BasePage):
    def __init__(self, url=None, *elements, **conditions):
        super(BingHomePage, self).__init__(
            url, *elements, **conditions
        )

        self.txt_search_box = WebTextBox(id='sb_form_q')
        self.btn_search_go = WebButton(id='sb_form_go')

    def search_with_keyword(self, keyword):
        self.txt_search_box.set(keyword)
        self.btn_search_go.click()

        return SearchResultsPage()
