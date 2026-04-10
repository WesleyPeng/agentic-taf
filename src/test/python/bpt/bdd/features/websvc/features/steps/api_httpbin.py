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
from taf.modeling.svc import RESTClient


@given('I have the API server url "{url}"')
def store_url_of_api_server(context, url):
    context.url = url


@when('I perform action "{action}" on the resource "{resource}" without payload')
def perform_action_against_api_server(
        context, action, resource
):
    with RESTClient(context.url) as client:
        op = getattr(client, str.lower(action))

        if op:
            context.response = op(resource)
        else:
            context.response = client.decode(
                '{status_code: None, content: None}'
            )


@then('I get the status code "{status_code}"')
def validate_status_code(context, status_code):
    assert context.response.status_code is not None
    assert context.response.status_code == int(status_code)


@then('I also get the key value pair "{key}" "{value}" in response')
def validate_response_content(context, key, value):
    assert context.response.content is not None
    assert str(
        getattr(
            RESTClient.decode(context.response.content),
            key
        )
    ) == value
