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

"""Page Object: Login page (dev mode — username, role, team form)."""

from typing import Any


class LoginPage:
    def __init__(self, page: Any):
        self.page = page

    @property
    def title(self):
        return self.page.locator('text=QA Platform Login')

    @property
    def username_input(self):
        return self.page.locator('#user')

    @property
    def role_select(self):
        return self.page.locator('#role')

    @property
    def team_input(self):
        return self.page.locator('#team')

    @property
    def login_button(self):
        return self.page.get_by_role('button', name='Login', exact=True)

    @property
    def sso_button(self):
        return self.page.locator('button:has-text("Dell SSO")')

    # Role labels in the Ant Design Select dropdown
    ROLE_LABELS = {
        'developer': 'Developer',
        'viewer': 'Viewer',
        'team-lead': 'Team Lead',
        'ci-service': 'CI Service',
        'platform-admin': 'Platform Admin',
    }

    def login(self, username='testuser', role='developer', team='platform-team'):
        """Fill the dev login form and submit."""
        self.username_input.fill(username)

        # Ant Design Select — click to open dropdown, then click the option by title
        label = self.ROLE_LABELS.get(role, role)
        self.role_select.click()
        self.page.locator(f'.ant-select-item-option[title="{label}"]').click()

        self.team_input.clear()
        self.team_input.fill(team)
        self.login_button.click()

    def is_visible(self):
        return self.title.is_visible(timeout=5000)
