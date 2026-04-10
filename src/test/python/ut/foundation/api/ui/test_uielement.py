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

from unittest import TestCase

from taf.foundation.api.ui import UIElement


class TestUIElement(TestCase):
    def setUp(self):
        self.child = None
        self.element = None

    def tearDown(self):
        del self.child
        del self.element

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            _ = UIElement().current

        with self.assertRaises(ValueError):
            UIElement(id='simple').exists(3)

    def test_abstract_methods(self):
        with self.assertRaises(NotImplementedError):
            UIElement(self.child, id='composite')

        with self.assertRaises(NotImplementedError):
            UIElement(element=self.child)

        with self.assertRaises(NotImplementedError):
            UIElement(parent=self.element)

        with self.assertRaises(NotImplementedError):
            _ = UIElement(id='simple').parent

        with self.assertRaises(NotImplementedError):
            _ = UIElement(id='simple').root

    def test_create_element(self):
        self.child = UIElement(id='simple')
        self.assertTrue(
            isinstance(self.child, UIElement)
        )
        for _ in self.child:
            self.fail('Not supposed to be iterable')

        self.assertNotEqual(
            self.child, UIElement(id='simple')
        )

        self.element = UIElement(
            self.child,
            id='composite'
        )
        self.assertTrue(
            isinstance(self.element, UIElement)
        )

        self.assertIn(self.child, self.element)
        self.assertIn(
            self.child,
            UIElement(element=self.element)
        )
