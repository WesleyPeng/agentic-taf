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

from behave import given, when, then

from bpt.pages import BingHomePage


@given('I am on the homepage "{url}"')
def step_give_i_am_on_the_home_page(context, url):
    context.home_page = BingHomePage(url)


@when('I search with keyword "{keyword}"')
def step_when_i_search_keyword(context, keyword):
    context.keyword = keyword
    context.search_results_page = \
        context.home_page.search_with_keyword(keyword)


@then('I get the first search result containing the keyword')
def step_then_i_get_the_first_search_record_containing_keyword(context):
    bag_of_keywords = str.split(
        context.search_results_page.text_of_first_record.lower()
    )

    assert (bag_of_keywords[0] in context.keyword.lower()) or (
            bag_of_keywords[-1] in context.keyword.lower()
    ), '"{}" not in "{}"'.format(
        context.keyword,
        context.search_results_page.text_of_first_record
    )
