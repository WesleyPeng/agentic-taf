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

from taf.foundation.utils import ConnectionCache


class WaitHandler:
    def __init__(
            self,
            handler=None,
            timeout=None
    ):
        self.handler = handler or ConnectionCache().current
        self.timeout = timeout or 30

    def wait(self, timeout=None):
        raise NotImplementedError(
            'Waits until the target is fully loaded'
        )
