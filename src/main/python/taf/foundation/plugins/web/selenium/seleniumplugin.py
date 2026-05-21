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

from taf.foundation.api.plugins import WebPlugin
from taf.foundation.plugins.web.selenium.browser import Browser
from taf.foundation.plugins.web.selenium.controls import Button
from taf.foundation.plugins.web.selenium.controls import CheckBox
from taf.foundation.plugins.web.selenium.controls import ComboBox
from taf.foundation.plugins.web.selenium.controls import Edit
from taf.foundation.plugins.web.selenium.controls import Frame
from taf.foundation.plugins.web.selenium.controls import Link
from taf.foundation.plugins.web.selenium.controls import RadioGroup
from taf.foundation.plugins.web.selenium.controls import Table
from taf.foundation.plugins.web.selenium.controls import Text


class SeleniumPlugin(WebPlugin):
    @property
    def controls(self):
        return [
            Button, CheckBox,
            ComboBox, Edit,
            Frame, Link,
            RadioGroup, Table,
            Text
        ]

    @property
    def browser(self):
        return Browser
