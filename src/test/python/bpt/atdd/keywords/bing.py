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

from robot.api import logger
from robot.version import get_version

from bpt.pages import BingHomePage
from bpt.pages import SearchResultsPage
from taf.modeling.web import Browser
from .robotlistener import RobotListener


class SearchKeywords:
    ROBOT_LIBRARY_VERSION = get_version()
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.browser = None
        self.home_page = None
        self.search_results_page = None

        self.listener = RobotListener(
            'selenium.webdriver.remote.remote_connection'
        )
        self.ROBOT_LIBRARY_LISTENER = self.listener

    def launch_browser(
            self,
            name='firefox',
            is_remote=False,
            enable_screenshot=False
    ):
        self.browser = Browser(
            name=name, is_remote=is_remote
        )

        if str(enable_screenshot).lower() not in ('false', 'no'):
            self.listener.enable_screenshot(
                self.browser
            )

    def close_browser(self):
        if self.browser:
            self.browser.close()

        self.listener.disable_screenshot()

    def i_am_on_home_page(self, url):
        self.home_page = BingHomePage(url)

    def i_search_with_keyword(self, keyword):
        self.search_results_page = \
            self.home_page.search_with_keyword(
                keyword
            )

    def i_get_the_first_search_record_containing_keyword(
            self, keyword
    ):
        assert isinstance(
            self.search_results_page, SearchResultsPage
        ), 'The search results page is displayed'

        bag_of_keywords = str.split(
            self.search_results_page.text_of_first_record.lower()
        )

        if (bag_of_keywords[0] in keyword.lower()) or (
                bag_of_keywords[-1] in keyword.lower()
        ):
            logger.info(
                'Succeed on searching keyword within bing.com',
                # html=True
            )
        else:
            logger.error(
                '"{}" not in "{}"'.format(
                    keyword,
                    self.search_results_page.text_of_first_record
                ),
                html=True
            )
