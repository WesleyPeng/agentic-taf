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
