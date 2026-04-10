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

from collections import namedtuple

from taf.foundation.api.ui.controls import Table as ITable
from taf.foundation.plugins.web.selenium.support.elementfinder import \
    ElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator
from taf.foundation.plugins.web.selenium.webelement import WebElement

RowItem = namedtuple(
    'RowItem', ['text', 'cells']
)


class Table(WebElement, ITable):
    def __init__(
            self, *elements, **conditions
    ):
        WebElement.__init__(
            self, *elements, **conditions
        )

        self._thead = None
        self._tfoot = None
        self._tbody = None

    def get_cell(self, row, column):
        return self.rows[row].cells[column]
        # return self.cells[row][column]

    @property
    def header(self):
        if not self._thead:
            self._thead = \
                self._get_table_element_by_tag(
                    'thead'
                )

        return self._thead

    @property
    def foot(self):
        if not self._tfoot:
            self._tfoot = \
                self._get_table_element_by_tag(
                    'tfoot'
                )

        return self._tfoot

    @property
    def body(self):
        if not self._tbody:
            self._tbody = \
                self._get_table_element_by_tag(
                    'tbody'
                )

        return self._tbody

    @property
    def rows(self):
        assert self.body

        return [
            RowItem(
                row.text, [
                    cell for cell in ElementFinder(
                        row
                    ).find_elements(
                        Locator.XPATH, './/td'
                    )
                ]
            ) for row in ElementFinder(
                self._tbody
            ).find_elements(
                Locator.XPATH, './/tr'
            )
        ]

    @property
    def cells(self):
        return [
            [row.cells] for row in self.rows
        ]

    @property
    def row_count(self):
        return len(self.rows)

    @property
    def columns(self):
        assert self.header

        return ElementFinder(
            self._thead
        ).find_elements(
            Locator.XPATH,
            './/tr/th'
        )

    @property
    def column_count(self):
        if self.header:
            return len(self.columns)

        _rows = self.rows
        if _rows:
            return len(_rows[-1].cells)

        raise RuntimeError('N/A')

    def _get_table_element_by_tag(
            self,
            tag_name
    ):
        assert self.exists()

        return ElementFinder(
            self.object
        ).find_elements(
            Locator.XPATH,
            './/{}'.format(tag_name)
        )[-1]
