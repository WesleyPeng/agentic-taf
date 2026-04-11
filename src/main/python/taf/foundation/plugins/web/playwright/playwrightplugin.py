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

from taf.foundation.api.plugins import WebPlugin
from taf.foundation.plugins.web.playwright.browser import Browser
from taf.foundation.plugins.web.playwright.controls import Button
from taf.foundation.plugins.web.playwright.controls import Edit
from taf.foundation.plugins.web.playwright.controls import Link
from taf.foundation.plugins.web.playwright.controls import Text


class PlaywrightPlugin(WebPlugin):
    @property
    def controls(self):
        return [
            Button, Edit, Link, Text,
        ]

    @property
    def browser(self):
        return Browser
