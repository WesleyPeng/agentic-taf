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

from taf.modeling.web import WebLink
from .basepage import BasePage


class SearchResultsPage(BasePage):
    def __init__(self, url=None, *elements, **conditions):
        super(SearchResultsPage, self).__init__(
            url, *elements, **conditions
        )

        self.lnk_first_record = WebLink(
            tag='a',
            xpath='//div[@id="b_content"]/ol[@id="b_results"]/li//a'
        )

    @property
    def text_of_first_record(self):
        return self.lnk_first_record.text
