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

from taf.foundation.api.plugins.baseplugin import BasePlugin
from taf.foundation.api.plugins import ChaosPlugin
from taf.foundation.api.chaos.client import Client, Fault, Probe


class TestChaosPluginInterface(TestCase):
    """Tests for ChaosPlugin interface."""

    def test_uses_baseplugin_metaclass(self):
        self.assertIsInstance(ChaosPlugin, BasePlugin)

    def test_has_plugins_registry(self):
        self.assertTrue(hasattr(ChaosPlugin, 'plugins'))
        self.assertIsInstance(ChaosPlugin.plugins, dict)

    def test_client_raises(self):
        with self.assertRaises(NotImplementedError):
            ChaosPlugin().client


class TestChaosBaseClient(TestCase):
    """Tests for chaos base client abstract methods."""

    def test_init(self):
        client = Client(namespace='test-ns')
        self.assertEqual(client.namespace, 'test-ns')

    def test_inject_raises(self):
        client = Client()
        with self.assertRaises(NotImplementedError):
            client.inject(Fault('test'), 'target')

    def test_verify_raises(self):
        client = Client()
        with self.assertRaises(NotImplementedError):
            client.verify(Probe('test'), 'target')

    def test_cleanup_raises(self):
        client = Client()
        with self.assertRaises(NotImplementedError):
            client.cleanup(Fault('test'), 'target')


class TestFaultAndProbeBase(TestCase):
    """Tests for Fault and Probe base classes."""

    def test_fault_repr(self):
        fault = Fault('test_fault')
        self.assertEqual(repr(fault), 'Fault(test_fault)')
        self.assertEqual(fault.name, 'test_fault')

    def test_probe_repr(self):
        probe = Probe('test_probe')
        self.assertEqual(repr(probe), 'Probe(test_probe)')
        self.assertEqual(probe.name, 'test_probe')

    def test_fault_params(self):
        fault = Fault('test', key='value')
        self.assertEqual(fault.params, {'key': 'value'})
