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

from taf.foundation.api.ui.controls import RadioGroup as IRadioGroup
from taf.foundation.plugins.web.selenium.controls.edit import Edit
from taf.foundation.plugins.web.selenium.controls.listitem import ListItem
from taf.foundation.plugins.web.selenium.support.elementfinder import \
    ElementFinder
from taf.foundation.plugins.web.selenium.support.locator import Locator
from taf.foundation.plugins.web.selenium.webelement import WebElement

RadioButton = namedtuple(
    'RadioButton', ['option', 'label']
)


class RadioGroup(WebElement, IRadioGroup):
    def __init__(
            self, *elements, **conditions
    ):
        conditions.setdefault('tag', 'form')

        _options_kwarg = 'option'
        _opt_label_kwarg = 'label'

        self._options_tag = conditions.pop(
            _options_kwarg
        ) if _options_kwarg in conditions else 'input'

        self._label_tag = conditions.pop(
            _opt_label_kwarg
        ) if _options_kwarg in conditions else _opt_label_kwarg

        WebElement.__init__(self, *elements, **conditions)

    def set(self, value):
        if str(value).isdigit() and (
                int(value) < len(list(self.items))
        ):
            list(self.items)[int(value)].option.select()
        else:
            for item in self.items:
                if (
                        value == item.option.current.get_attribute('value')
                ) or (value == item.label.text):
                    item.option.select()
                    break
            else:
                raise ValueError(
                    'Could not locate element with value: {}'.format(
                        value
                    )
                )

    @property
    def value(self):
        if self.exists():
            for item in self.items:
                if item.option.is_selected:
                    return item.label.text

        return r''

    @property
    def items(self):
        if not self._children:
            if self.exists():
                _finder = ElementFinder(self.object).find_elements
                self._children = [  # type: ignore[assignment]
                    RadioButton(
                        ListItem(element=option, parent=self),
                        Edit(element=label, parent=self)
                    ) for option, label in zip(
                        _finder(
                            Locator.XPATH,
                            './/{}[@type=radio]'.format(
                                self._options_tag
                            )
                        ),
                        _finder(
                            Locator.XPATH,
                            './/{}'.format(self._label_tag)
                        )
                    )
                ]

        return (child for child in self._children)
