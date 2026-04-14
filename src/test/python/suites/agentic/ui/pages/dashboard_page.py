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

"""Page Object: Dashboard page (health indicators, environment summary)."""

from typing import Any


class DashboardPage:
    def __init__(self, page: Any):
        self.page = page

    @property
    def heading(self):
        return self.page.get_by_role('heading', name='Dashboard')

    def is_loaded(self):
        return self.heading.is_visible(timeout=10000)

    def get_text(self):
        return self.page.content()
