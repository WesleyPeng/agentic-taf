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

from functools import reduce


class ElementFinder:
    def __init__(self, anchor):
        self.anchor = anchor

    @property
    def elements_finding_strategies(self):
        # return {}
        raise NotImplementedError(
            'Element finding strategies'
        )

    @property
    def excluded_screening_locators(self):
        return ()

    def find_element(
            self, *locators, **constraints
    ):
        try:
            index = int(constraints.pop('index'))
        except Exception:
            index = 0

        try:
            elements: list = []

            conditions = {
                locator: value
                for locator, value in locators
                if locator not in self.excluded_screening_locators
            }

            conditions.update(**constraints)

            for locator, value in locators:
                elements = reduce(
                    lambda acc, current:
                    acc if current in acc else acc + [current],
                    [elements, ] + self.find_elements_meet_conditions(
                        *self.find_elements(locator, value),
                        **conditions
                    )
                )
        except Exception:
            pass
        else:
            if elements and (index < len(elements)):
                return elements[index]

        return None

    def find_elements(self, locator, value):
        elements = []

        finder = getattr(
            self.anchor,
            self.elements_finding_strategies.get(locator),
            None
        )

        if finder and callable(finder):
            try:
                elements += finder(value)
            except Exception:
                pass

        return elements

    def find_elements_meet_conditions(
            self, *elements, **conditions
    ):
        elements_met_conditions = []

        for element in elements:
            for key, value in conditions.items():
                try:
                    attr_value = self.get_element_attribute(
                        element, key
                    )
                except Exception:
                    pass  # TBH
                else:
                    if attr_value and value and str(
                            attr_value
                    ).upper() != str(value).upper():
                        break
            else:
                elements_met_conditions.append(element)

        return elements_met_conditions

    def get_element_attribute(
            self, element, attribute_name
    ):
        return element.get_attribute(
            '{}'.format(attribute_name)
        ) or getattr(
            element,
            '{}'.format(attribute_name),
            None
        )
