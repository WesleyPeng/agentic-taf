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

from behave import fixture

from taf.modeling.web import Browser


@fixture
def web_browser_fixture(context, *args, **kwargs):
    browser = None

    try:
        userdata = context.config.userdata

        browser = Browser(
            name=userdata.get('browser', 'firefox'),
            is_remote=userdata.get(
                'is_remote', 'False'
            ).lower() in ['true', 'yes']
        )

        context.browser = browser

        yield browser
    finally:
        if browser:
            browser.close()
