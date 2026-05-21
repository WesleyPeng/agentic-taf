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

from unittest import TestCase

from taf.foundation import ServiceLocator
from taf.foundation.api.ui.controls import Button
from taf.foundation.api.ui.web import Browser


class TestServiceLocator(TestCase):
    def setUp(self):
        self.conf = ServiceLocator()

    def test_browser(self):
        browser = self.conf.get_app_under_test()
        self.assertIsNot(
            browser, Browser
        )
        self.assertTrue(
            issubclass(browser, Browser)
        )

    def test_modeled_button(self):
        button = self.conf.get_modeled_control(
            Button
        )

        self.assertIsNot(
            button, Button
        )
        self.assertTrue(
            issubclass(button, Button)
        )
