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

from selenium.webdriver.common.by import By

from taf.foundation.api.ui.support import ElementFinder as IElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator


# Mapping from Locator enum values to Selenium By strategies
_LOCATOR_TO_BY = {
    Locator.ID: By.ID,
    Locator.XPATH: By.XPATH,
    Locator.NAME: By.NAME,
    Locator.TAG: By.TAG_NAME,
    Locator.CSS: By.CSS_SELECTOR,
    Locator.CLASSNAME: By.CLASS_NAME,
    Locator.TEXT: By.LINK_TEXT,
    Locator.TEXT_CONTAINS: By.PARTIAL_LINK_TEXT,
}


class ElementFinder(IElementFinder):
    def __init__(self, anchor):
        super().__init__(anchor)

    @property
    def elements_finding_strategies(self):
        # Retained for interface compatibility; not used by find_elements
        return {
            locator: by for locator, by in _LOCATOR_TO_BY.items()
        }

    @property
    def excluded_screening_locators(self):
        return Locator.XPATH, Locator.CSS

    def find_elements(self, locator, value):
        by = _LOCATOR_TO_BY.get(locator)
        if by is None:
            return []

        try:
            return self.anchor.find_elements(by, value)
        except Exception:
            return []
