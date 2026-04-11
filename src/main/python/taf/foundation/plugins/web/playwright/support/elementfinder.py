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
from taf.foundation.plugins.web.playwright.support.locator import Locator


class ElementFinder(IElementFinder):
    def __init__(self, anchor):
        super().__init__(anchor)

    @property
    def elements_finding_strategies(self):
        return {
            Locator.ID: 'id',
            Locator.XPATH: 'xpath',
            Locator.NAME: 'name',
            Locator.TAG: 'tag',
            Locator.CSS: 'css',
            Locator.CLASSNAME: 'class',
            Locator.TEXT: 'text',
            Locator.TEXT_CONTAINS: 'text_contains',
        }

    @property
    def excluded_screening_locators(self):
        return Locator.XPATH, Locator.CSS

    def find_elements(self, locator, value):
        if self.anchor is None:
            return []

        selectors = {
            Locator.ID: '#{}'.format(value),
            Locator.XPATH: 'xpath={}'.format(value),
            Locator.NAME: '[name="{}"]'.format(value),
            Locator.TAG: value,
            Locator.CSS: value,
            Locator.CLASSNAME: '.{}'.format(value),
            Locator.TEXT: 'text="{}"'.format(value),
            Locator.TEXT_CONTAINS: 'text={}'.format(value),
        }

        selector = selectors.get(locator)
        if not selector:
            return []

        try:
            locator_obj = self.anchor.locator(selector)
            count = locator_obj.count()
            return [locator_obj.nth(i) for i in range(count)]
        except Exception:
            return []
