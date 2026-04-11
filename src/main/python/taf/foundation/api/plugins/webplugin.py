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
