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

from urllib.parse import quote
from unittest import TestCase

from taf.foundation.plugins.web.selenium.browser import Browser as SeBrowser
from taf.foundation.plugins.web.selenium.controls import Button as SeButton
from taf.foundation.plugins.web.selenium.controls import Edit as SeEdit
from taf.foundation.plugins.web.selenium.controls import Link as SeLink
from taf.modeling.web import Browser
from taf.modeling.web import WebButton
from taf.modeling.web import WebLink
from taf.modeling.web import WebTextBox

_TEST_HTML = '''<!DOCTYPE html><html><body>
<form id="search_form">
<input type="text" id="search_box" name="q"/>
<input type="submit" id="search_btn" name="go" class="btn-search" value="Search"/>
</form>
<a id="result_link" href="about:blank">Result</a>
</body></html>'''

_TEST_PAGE = 'data:text/html,' + quote(_TEST_HTML)


class TestModelingTypes(TestCase):
    def setUp(self):
        self.browser = Browser(name='chrome', headless=True)

    def tearDown(self):
        self.browser.close()
        del self.browser

    def test_web_browser(self):
        self.assertTrue(
            issubclass(
                Browser,
                SeBrowser
            )
        )

        self.assertIsInstance(
            self.browser,
            SeBrowser
        )

        another_browser = Browser(
            name='chrome', identifier='another', headless=True
        )
        another_browser.launch(_TEST_PAGE)

        self.browser.activate()
        self.browser.launch(_TEST_PAGE)
        self.browser.maximize()

        another_browser.close()

    def test_web_controls(self):
        self.assertTrue(
            issubclass(
                WebButton,
                SeButton
            )
        )

        self.browser.launch(_TEST_PAGE)
        self.browser.maximize()

        txt_search = WebTextBox(
            id='search_box'
        )
        self.assertIsInstance(
            txt_search,
            SeEdit
        )

        btn_go = WebButton(
            xpath='//input[@id="search_btn"]',
            name='go',
            tag='input',
            classname='btn-search'
        )
        self.assertIsInstance(
            btn_go,
            SeButton
        )

        btn_go_with_id = WebButton(id='search_btn')

        self.assertEqual(
            btn_go.object._id,
            btn_go_with_id.object._id
        )

        _value = 'agentic-taf'
        txt_search.set(_value)

        self.assertEqual(
            txt_search.value,
            _value
        )

        lnk_item = WebLink(
            xpath='//a[@id="result_link"]',
            tag='a',
        )

        self.assertIsInstance(
            lnk_item,
            SeLink
        )

        lnk_item.click()
