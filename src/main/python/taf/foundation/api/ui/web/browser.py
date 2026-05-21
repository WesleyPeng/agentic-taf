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

from taf.foundation.api.ui import AUT


class Browser(AUT):
    def __init__(
            self,
            name='firefox',
            identifier=None,
            **kwargs
    ):
        super().__init__(
            name, identifier, **kwargs
        )

    @staticmethod
    def launch(url='about:blank', **kwargs):  # type: ignore[override]
        raise NotImplementedError(
            'Web browser navigates to specific page'
        )

    def maximize(self):
        raise NotImplementedError(
            'Maximize the current browser'
        )

    def sync(self, timeout=30):
        raise NotImplementedError(
            'Synchronization until browser is fully loaded or timeout'
        )

    def _create_instance(self, name, **kwargs):
        raise NotImplementedError(
            'Create web browser instance (type={})'.format(
                name
            )
        )
