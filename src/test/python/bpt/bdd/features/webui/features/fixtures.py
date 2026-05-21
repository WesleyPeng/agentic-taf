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
