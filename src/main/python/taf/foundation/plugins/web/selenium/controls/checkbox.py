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

from taf.foundation.api.ui.controls import CheckBox as ICheckBox
from taf.foundation.plugins.web.selenium.webelement import WebElement


class CheckBox(WebElement, ICheckBox):
    def tick(self):
        if not self.state:
            self.toggle()

    def untick(self):
        if self.state:
            self.toggle()

    def toggle(self):
        self.current.click()

    @property
    def state(self):
        assert self.exists() and self.object.is_enabled(), \
            'N/A - invisible/disabled element'

        _checked = self.object.get_attribute('checked')

        return _checked and ('false' != _checked)
