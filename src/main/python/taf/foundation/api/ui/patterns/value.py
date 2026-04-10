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

from .basepattern import BasePattern


class Value(BasePattern):
    def set(self, value):
        raise NotImplementedError(
            'Set new value for the element'
        )

    @property
    def value(self):
        raise NotImplementedError(
            'Get value of the element'
        )

    @property
    def is_read_only(self):
        raise NotImplementedError(
            'Element is read only'
        )
