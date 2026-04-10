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
