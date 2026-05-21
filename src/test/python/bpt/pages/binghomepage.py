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

from taf.modeling.web import WebButton
from taf.modeling.web import WebTextBox
from .basepage import BasePage
from .searchresultspage import SearchResultsPage


class BingHomePage(BasePage):
    def __init__(self, url=None, *elements, **conditions):
        super().__init__(
            url, *elements, **conditions
        )

        self.txt_search_box = WebTextBox(id='sb_form_q')
        self.btn_search_go = WebButton(id='sb_form_go')

    def search_with_keyword(self, keyword):
        self.txt_search_box.set(keyword)
        self.btn_search_go.click()

        return SearchResultsPage()
