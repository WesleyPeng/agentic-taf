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

from taf.foundation.api.ui.controls import ComboBox as IComboBox
from taf.foundation.plugins.web.selenium.controls.listitem import ListItem
from taf.foundation.plugins.web.selenium.support.elementfinder import \
    ElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator
from taf.foundation.plugins.web.selenium.webelement import WebElement


class ComboBox(WebElement, IComboBox):
    def __init__(self, *elements, **conditions):
        conditions.setdefault('tag', 'select')

        _options_kwarg = 'option'
        _multi_selection_kwarg = 'multiple'

        self._options_tag = conditions.pop(
            _options_kwarg
        ) if _options_kwarg in conditions else _options_kwarg

        self._multi_selection_attr = conditions.pop(
            _multi_selection_kwarg
        ) if _multi_selection_kwarg in conditions else _multi_selection_kwarg

        WebElement.__init__(
            self, *elements, **conditions
        )

    def set(self, value):
        if isinstance(value, (list, tuple)):
            if not self.can_select_multiple:
                raise RuntimeError(
                    'Multi-selection is not supported'
                )
        else:
            value = [value]

        for val in value:
            if str(val).isdigit():
                list(self.options)[int(val)].select()

                continue
            else:
                for opt in self.options:
                    if (
                            val == opt.current.get_attribute('value')
                    ) or (val == opt.object.text):
                        opt.select()

                        break
                else:
                    raise ValueError(
                        'Could not locate element with value: {}'.format(
                            val
                        )
                    )

    @property
    def value(self):
        if self.exists():
            return ';'.join(
                opt.object.text
                for opt in self.options
                if opt.object.is_selected()
            )

        return r''

    @property
    def options(self):
        if not self._children:
            if self.exists():
                self._children = [
                    ListItem(element=element, parent=self)
                    for element in ElementFinder(
                        self.object
                    ).find_elements(
                        Locator.XPATH,
                        './/{}'.format(self._options_tag)
                    ) if element  # and element.text
                ]

        return (child for child in self._children)

    @property
    def is_read_only(self):
        assert self.exists(), 'N/A - invisible element'

        return not self.object.is_enabled()

    @property
    def can_select_multiple(self):
        return self._get_attribute(
            self._multi_selection_attr
        )

    @property
    def is_selection_required(self):
        return self._get_attribute('required')

    def _get_attribute(self, name):
        assert not self.is_read_only, \
            'N/A - disabled element'

        attr_value = self.object.get_attribute(
            name
        )
        return attr_value and attr_value != 'false'
