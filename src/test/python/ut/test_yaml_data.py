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
