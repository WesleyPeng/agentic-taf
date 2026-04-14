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

"""Page Object: Chat page (message input, response area)."""

from typing import Any


class ChatPage:
    def __init__(self, page: Any):
        self.page = page

    @property
    def heading(self):
        return self.page.get_by_role('heading', name='Chat')

    @property
    def message_input(self):
        return self.page.locator('textarea, input[type="text"]').last

    def is_loaded(self):
        return self.heading.is_visible(timeout=10000)

    def navigate(self):
        self.page.click('a:has-text("Chat")')
