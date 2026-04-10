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

import os
import unittest

from taf.foundation.utils import YAMLData


class TestYAMLData(unittest.TestCase):
    def setUp(self):
        self.data = YAMLData()

    def tearDown(self):
        self.data = None

    def test_updating_node_with_valid_data(self):
        key = 'unittest'
        value = 'dummy data'

        self.data[key] = []
        self.data[key] += [value]
        self.assertIn(
            value,
            self.data[key]
        )
        self.data.unittest.pop()

        self.data[key] = value
        self.assertEqual(
            getattr(self.data, key),
            value
        )

        self.data += {
            key: self._testMethodName,
            'other': dict(
                key=self.__class__.__name__
            )
        }

        self.assertEqual(
            self.data[key],
            self._testMethodName
        )

        self.assertEqual(
            self.data.other.key,
            self.__class__.__name__
        )

    def test_updating_node_with_invalid_data(self):
        self.data.key = {}

        with self.assertRaises(ValueError):
            self.data.key += 'value'

        with self.assertRaises(ValueError):
            self.data.key += ['value']

    def test_dump_load(self):
        file_path = os.path.join(
            os.path.dirname(__file__),
            'data.yaml'
        )

        self.data += {'key': 'value'}
        self.data.dump(file_path)
        self.assertIsInstance(
            YAMLData.load(file_path),
            YAMLData
        )

        os.remove(file_path)
