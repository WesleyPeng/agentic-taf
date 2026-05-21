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

from taf.foundation.api.ui.controls import ListItem as IListItem
from taf.foundation.plugins.web.selenium.webelement import WebElement


class ListItem(WebElement, IListItem):
    def select(self):
        if not self.is_selected:
            self.object.click()

    def deselect(self):
        if self.is_selected:
            self.object.click()

    @property
    def is_selected(self):
        assert self.exists(), 'N/A - item is not available'

        return self.object.is_selected()
