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

import json
import unittest

from taf.foundation.api.svc.REST import Client
from taf.foundation.utils import YAMLData


class TestClientCodecMethods(unittest.TestCase):
    """Test the REST Client encode/decode methods."""

    def test_decode_valid_json_dict(self):
        json_str = '{"name": "test", "value": 42}'
        result = Client.decode(json_str)
        self.assertIsInstance(result, YAMLData)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.value, 42)

    def test_decode_valid_json_list(self):
        json_str = '[1, 2, 3]'
        result = Client.decode(json_str)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1, 2, 3])

    def test_decode_invalid_json(self):
        result = Client.decode("not valid json")
        self.assertEqual(result, {})

    def test_decode_empty_string(self):
        result = Client.decode("")
        self.assertEqual(result, {})

    def test_encode_dict(self):
        data = {"key": "value", "number": 1}
        result = Client.encode(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")
        self.assertEqual(parsed["number"], 1)

    def test_encode_yaml_data(self):
        data = YAMLData(name="test", items=["a", "b"])
        result = Client.encode(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["name"], "test")
        self.assertEqual(parsed["items"], ["a", "b"])

    def test_encode_nested_dict(self):
        data = {"outer": {"inner": "value"}}
        result = Client.encode(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["outer"]["inner"], "value")

    def test_encode_list(self):
        data = [{"a": 1}, {"b": 2}]
        result = Client.encode(data)
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["a"], 1)

    def test_encode_primitive(self):
        result = Client.encode("hello")
        self.assertEqual(json.loads(result), "hello")


class TestClientInit(unittest.TestCase):
    """Test the REST Client initialization."""

    def test_init_basic_url(self):
        client = Client("http://example.com")
        self.assertEqual(client.params["url"], "http://example.com")
        self.assertIsNone(client.params["username"])

    def test_init_with_credentials(self):
        client = Client(
            "http://example.com",
            username="user",
            password="pass"
        )
        self.assertEqual(client.params["username"], "user")
        self.assertEqual(client.params["password"], "pass")

    def test_init_with_port_validation(self):
        client = Client("http://example.com", port=8080)
        self.assertIn("url", client.params)

    def test_init_invalid_port(self):
        with self.assertRaises(AssertionError):
            Client("http://example.com", port="not_a_number")

    def test_abstract_methods_raise(self):
        client = Client("http://example.com")

        # HTTP verbs are intentionally abstract — subclasses MUST
        # implement them. Calling on the base class is a contract error.
        with self.assertRaises(NotImplementedError):
            client.get("/resource")

        with self.assertRaises(NotImplementedError):
            client.post("/resource")

        with self.assertRaises(NotImplementedError):
            client.put("/resource")

        with self.assertRaises(NotImplementedError):
            client.delete("/resource")

        with self.assertRaises(NotImplementedError):
            client.patch("/resource")

    def test_context_manager_no_raise(self):
        # __exit__ must NOT raise — Python's `with` machinery calls it
        # unconditionally on block exit. The base close() is a no-op so
        # bare-Client `with` blocks work; subclasses override close() to
        # release transport resources (httpx.Client.close(), etc.).
        with Client("http://example.com") as client:
            self.assertIsNotNone(client.params)
        # Explicit close() is also safe on the base class.
        Client("http://example.com").close()


if __name__ == '__main__':
    unittest.main()
