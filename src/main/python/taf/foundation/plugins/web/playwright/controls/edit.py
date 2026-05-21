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

from taf.foundation.api.ui.controls import Edit as IEdit
from taf.foundation.plugins.web.playwright.webelement import WebElement


class Edit(WebElement, IEdit):
    @property
    def value(self):
        if self.object:
            return self.object.input_value()
        return ''

    def set(self, value):
        if self.object:
            self.object.fill(str(value))
