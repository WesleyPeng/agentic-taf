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


class Text(BasePattern):
    def get_selection(self):
        raise NotImplementedError(
            'Get the selected text of the element'
        )

    @property
    def text(self):
        raise NotImplementedError(
            'Element visible text'
        )

    @property
    def supports_text_selection(self):
        raise NotImplementedError(
            'Element supports text selection'
        )
