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
