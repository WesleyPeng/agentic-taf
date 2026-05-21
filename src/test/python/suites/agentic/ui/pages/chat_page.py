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
