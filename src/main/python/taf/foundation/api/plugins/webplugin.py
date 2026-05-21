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

from .baseplugin import BasePlugin


class WebPlugin(metaclass=BasePlugin):

    def __init__(self):
        super().__init__()

    @property
    def controls(self):
        raise NotImplementedError(
            'Web controls'
        )

    @property
    def browser(self):
        raise NotImplementedError(
            'The browser type'
        )

    @property
    def app_under_test(self):
        return self.browser
