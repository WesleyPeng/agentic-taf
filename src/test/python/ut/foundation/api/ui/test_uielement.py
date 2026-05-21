# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Wesley Peng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
