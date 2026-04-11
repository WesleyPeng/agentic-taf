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
