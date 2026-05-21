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
