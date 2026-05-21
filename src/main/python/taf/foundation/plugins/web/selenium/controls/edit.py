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
from taf.foundation.plugins.web.selenium.webelement import WebElement


class Edit(WebElement, IEdit):
    def get_selection(self):
        raise RuntimeError(
            'Unsupported feature for web element'
        )

    @property
    def text(self):
        if self.exists():
            return self.object.text

        return r''

    @property
    def supports_text_selection(self):
        return True

    def set(self, value):
        assert not self.is_read_only, \
            'N/A - read-only element'

        self.object.clear()
        self.object.send_keys(value)

    @property
    def value(self):
        if self.exists():
            return self.object.get_attribute('value')

        return r''

    @property
    def is_read_only(self):
        assert self.exists(), 'N/A - invisible element'

        return not self.object.is_enabled()
