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

import importlib
from unittest import TestCase, skipUnless
from unittest.mock import patch, MagicMock

from taf.foundation.api.plugins import ChaosPlugin

_has_kubernetes = importlib.util.find_spec('kubernetes') is not None


@skipUnless(_has_kubernetes, 'kubernetes not installed')
class TestK8sChaosPlugin(TestCase):
    """Tests for K8sChaosPlugin registration."""

    def test_registered_in_plugins(self):
        from taf.foundation.plugins.chaos.k8s.k8schaosplugin import K8sChaosPlugin
        self.assertIn('k8schaosplugin', ChaosPlugin.plugins)
        self.assertTrue(issubclass(K8sChaosPlugin, ChaosPlugin))


@skipUnless(_has_kubernetes, 'kubernetes not installed')
class TestK8sChaosClient(TestCase):
    """Tests for K8sChaosClient with mocked kubernetes API."""

    @patch('taf.foundation.plugins.chaos.k8s.k8schaosclient.config')
    @patch('taf.foundation.plugins.chaos.k8s.k8schaosclient.client')
    def _make_client(self, mock_client_mod, mock_config):
        from taf.foundation.plugins.chaos.k8s.k8schaosclient import K8sChaosClient
        return K8sChaosClient(namespace='test-ns'), mock_client_mod

    def test_init(self):
        client, _ = self._make_client()
        self.assertEqual(client.namespace, 'test-ns')

    def test_inject_pod_kill(self):
        client, mock_client_mod = self._make_client()
        from taf.foundation.plugins.chaos.k8s.faults import PodKill

        mock_pod = MagicMock()
        mock_pod.metadata.name = 'agent-pod-1'
        mock_client_mod.CoreV1Api.return_value.list_namespaced_pod.return_value.items = [mock_pod]

        fault = PodKill(label_selector='app=agent')
        result = client.inject(fault, 'agent')
        self.assertTrue(result['injected'])
        self.assertEqual(result['killed_pods'], ['agent-pod-1'])

    def test_inject_network_partition(self):
        client, mock_client_mod = self._make_client()
        from taf.foundation.plugins.chaos.k8s.faults import NetworkPartition

        fault = NetworkPartition(label_selector='app=agent')
        result = client.inject(fault, 'agent')
        self.assertTrue(result['injected'])
        mock_client_mod.NetworkingV1Api.return_value.create_namespaced_network_policy.assert_called_once()

    def test_inject_flux_suspend(self):
        client, mock_client_mod = self._make_client()
        from taf.foundation.plugins.chaos.k8s.faults import FluxSuspend

        fault = FluxSuspend(kustomization_name='agent-deployment')
        result = client.inject(fault, 'agent')
        self.assertTrue(result['injected'])
        mock_client_mod.CustomObjectsApi.return_value.patch_namespaced_custom_object.assert_called_once()

    def test_verify_http_health(self):
        client, _ = self._make_client()
        from taf.foundation.plugins.chaos.k8s.probes import HttpHealthProbe

        probe = HttpHealthProbe(url='http://agent/health')
        with patch('taf.foundation.plugins.chaos.k8s.probes.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            self.assertTrue(client.verify(probe, 'agent'))

    def test_verify_k8s_ready(self):
        client, mock_client_mod = self._make_client()
        from taf.foundation.plugins.chaos.k8s.probes import K8sReadyProbe

        mock_pod = MagicMock()
        mock_pod.status.phase = 'Running'
        mock_cs = MagicMock()
        mock_cs.ready = True
        mock_pod.status.container_statuses = [mock_cs]
        mock_client_mod.CoreV1Api.return_value.list_namespaced_pod.return_value.items = [mock_pod]

        probe = K8sReadyProbe(label_selector='app=agent', min_ready=1)
        self.assertTrue(client.verify(probe, 'agent'))

    def test_cleanup_network_partition(self):
        client, mock_client_mod = self._make_client()
        from taf.foundation.plugins.chaos.k8s.faults import NetworkPartition

        fault = NetworkPartition(label_selector='app=agent')
        client.cleanup(fault, 'agent')
        mock_client_mod.NetworkingV1Api.return_value.delete_namespaced_network_policy.assert_called_once()

    def test_inject_unsupported_fault_raises(self):
        client, _ = self._make_client()
        from taf.foundation.api.chaos.client import Fault

        with self.assertRaises(ValueError):
            client.inject(Fault('unknown'), 'target')
