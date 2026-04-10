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
from unittest import skip

from taf.foundation.plugins.web.selenium.browser import Browser as SeBrowser
from taf.foundation.plugins.web.selenium.controls import Button as SeButton
from taf.foundation.plugins.web.selenium.controls import Edit as SeEdit
from taf.foundation.plugins.web.selenium.controls import Link as SeLink
from taf.modeling.web import Browser
from taf.modeling.web import WebButton
from taf.modeling.web import WebLink
from taf.modeling.web import WebTextBox
# from applitools.eyes import Eyes


@skip('Temporarily ignore WebUI tests')
class TestModelingTypes(TestCase):
    # eyes = Eyes()

    # @classmethod
    # def setUpClass(cls):
    #     cls.eyes.api_key = 'secret'
    #
    # @classmethod
    # def tearDownClass(cls):
    #     cls.eyes.abort_if_not_closed()

    def setUp(self):
        self.browser = Browser()
        # self.eyes.open(
        #     self.browser.cache.current,
        #     'bing.com',
        #     'UT',
        #     {'width': 1600, 'height': 900}
        # )

    def tearDown(self):
        # self.eyes.close()

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

        another_browser = Browser(identifier='another')
        another_browser.launch('http://www.microsoft.com')

        self.browser.activate()
        self.browser.launch('http://www.bing.com')
        self.browser.maximize()
        # self.eyes.check_window('browser')

        another_browser.close()

    def test_web_controls(self):
        self.assertTrue(
            issubclass(
                WebButton,
                SeButton
            )
        )

        self.browser.launch('http://www.bing.com')
        self.browser.maximize()

        # self.eyes.check_window('bing home page')

        txt_search = WebTextBox(
            id='sb_form_q'
        )
        self.assertIsInstance(
            txt_search,
            SeEdit
        )

        btn_go = WebButton(
            xpath='//input[@id="sb_form_go"]',
            name='go',
            tag='input',
            classname='b_searchboxSubmit'
        )
        self.assertIsInstance(
            btn_go,
            SeButton
        )

        btn_go_with_id = WebButton(id='sb_form_go')

        self.assertEqual(
            btn_go.object._id,
            btn_go_with_id.object._id
        )

        _value = 'wesleypeng+uiXautomation'
        txt_search.set(_value)
        btn_go.click()

        self.assertEqual(
            txt_search.value,
            _value
        )

        # self.eyes.check_window('search results')

        lnk_item = WebLink(
            xpath='//div[@id="b_content"]/ol[@id="b_results"]/li//a',
            tag='a',
        )

        self.assertIsInstance(
            lnk_item,
            SeLink
        )

        lnk_item.click()
