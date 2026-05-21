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

from taf.foundation.api.ui.support import Locator as LocatorEnum


class Locator(LocatorEnum):
    ID = 'id'
    XPATH = 'xpath'
    NAME = 'name'
    TAG = 'tag_name'
    CLASSNAME = 'class'
    CSS = 'css'
    TEXT = 'text'
    TEXT_CONTAINS = 'innerText'

    @classmethod
    def prioritized_locators(cls):
        return (
            Locator.ID, Locator.XPATH,
            Locator.CSS, Locator.NAME,
            Locator.CLASSNAME, Locator.TEXT,
            Locator.TEXT_CONTAINS, Locator.TAG,
        )
