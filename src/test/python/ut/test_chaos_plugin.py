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
