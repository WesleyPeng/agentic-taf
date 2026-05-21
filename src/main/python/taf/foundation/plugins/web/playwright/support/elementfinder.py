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
