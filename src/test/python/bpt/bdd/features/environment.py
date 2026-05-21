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

import sys

from allure import attach
from allure import attachment_type
from behave import use_fixture
from behave.textutil import text

from bpt.bdd.features.webui.features.fixtures import web_browser_fixture
from taf.modeling.web import Browser


class BehavePatch:
    def __init__(self, context, step):
        self.context, self.step = context, step

    def store_exception_context(self, exception):
        self.step.exception = exception
        self.step.exe_traceback = sys.exc_info()[2]

        self._insert_png_screenshot_to_allure_report(
            text(exception)
        )

    def _insert_png_screenshot_to_allure_report(
            self, name='screenshot'
    ):
        if Browser.current and self.context and self.step:
            try:
                attach(
                    name=name,
                    body=Browser.current.take_screenshot(),
                    attachment_type=attachment_type.PNG
                )
            except Exception:
                raise


def before_step(context, step):
    step.store_exception_context = BehavePatch(
        context, step
    ).store_exception_context


def before_tag(context, tag):
    if tag == 'bing.ui':
        use_fixture(
            web_browser_fixture, context
        )
