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

from taf.foundation.api.ui.support import ElementFinder as IElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator


class ElementFinder(IElementFinder):
    def __init__(self, anchor):
        super(ElementFinder, self).__init__(anchor)

    @property
    def elements_finding_strategies(self):
        return {
            Locator.ID: 'find_elements_by_id',
            Locator.XPATH: 'find_elements_by_xpath',
            Locator.NAME: 'find_elements_by_name',
            Locator.TAG: 'find_elements_by_tag_name',
            Locator.CSS: 'find_elements_by_css_selector',
            Locator.CLASSNAME: 'find_elements_by_class_name',
            Locator.TEXT: 'find_elements_by_link_text',
            Locator.TEXT_CONTAINS: 'find_elements_by_partial_link_text'
        }

    @property
    def excluded_screening_locators(self):
        return Locator.XPATH, Locator.CSS

    def find_elements(self, locator, value):
        return super(
            ElementFinder, self
        ).find_elements(
            locator, value
        )
