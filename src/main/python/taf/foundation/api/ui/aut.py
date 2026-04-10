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


class AUT(object):
    cache = None
    current = None

    def __init__(
            self,
            name=None,
            identifier=None,
            **kwargs
    ):
        if not AUT.cache:
            AUT.cache = ConnectionCache(identifier)

        self.id = self.cache.register(
            self._create_instance(name, **kwargs),
            identifier
        )

        AUT.current = self

    @staticmethod
    def launch(app_location, **kwargs):
        raise NotImplementedError(
            'Launch application'
        )

    def activate(self):
        if self.id != self.cache.current_key:
            self.cache.current_key = self.id

            AUT.current = self

    def take_screenshot(self):
        self.activate()

        return self.get_screenshot_data()

    def close(self):
        self.cache.close(self.id)

        if not self.cache.current:
            AUT.cache = None
            AUT.current = None

    def get_screenshot_data(self):
        raise NotImplementedError(
            'Get screenshot data from AUT'
        )

    def _create_instance(self, name, **kwargs):
        raise NotImplementedError(
            'Create instance of AUT'
        )
