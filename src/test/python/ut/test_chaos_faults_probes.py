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

from taf.foundation.plugins.chaos.k8s.faults import (
    PodKill, NetworkPartition, ResourcePressure, DNSFailure, FluxSuspend,
)
from taf.foundation.plugins.chaos.k8s.probes import (
    HttpHealthProbe, K8sReadyProbe, PrometheusProbe,
)


class TestFaultDefinitions(TestCase):
    """Tests for K8s fault definitions."""

    def test_pod_kill(self):
        f = PodKill(label_selector='app=agent', count=2)
        self.assertEqual(f.name, 'pod_kill')
        self.assertEqual(f.label_selector, 'app=agent')
        self.assertEqual(f.count, 2)
        self.assertIn('PodKill', repr(f))

    def test_network_partition(self):
        f = NetworkPartition(label_selector='app=agent')
        self.assertEqual(f.name, 'network_partition')
        self.assertEqual(f.block_cidr, '0.0.0.0/0')

    def test_resource_pressure(self):
        f = ResourcePressure(label_selector='app=agent', cpu='100m', memory='128Mi')
        self.assertEqual(f.cpu, '100m')
        self.assertEqual(f.memory, '128Mi')

    def test_dns_failure(self):
        f = DNSFailure(service_name='postgresql')
        self.assertEqual(f.service_name, 'postgresql')

    def test_flux_suspend(self):
        f = FluxSuspend(kustomization_name='agent-deployment')
        self.assertEqual(f.kustomization_name, 'agent-deployment')


class TestProbeDefinitions(TestCase):
    """Tests for K8s probe definitions."""

    def test_http_health_probe(self):
        p = HttpHealthProbe(url='http://localhost/health', expected_status=200)
        self.assertEqual(p.name, 'http_health')
        self.assertEqual(p.url, 'http://localhost/health')
        self.assertEqual(p.expected_status, 200)

    def test_k8s_ready_probe(self):
        p = K8sReadyProbe(label_selector='app=agent', min_ready=2)
        self.assertEqual(p.label_selector, 'app=agent')
        self.assertEqual(p.min_ready, 2)

    def test_prometheus_probe(self):
        p = PrometheusProbe(
            query='up{job="agent"}', threshold=1.0,
            url='http://prometheus:9090',
        )
        self.assertEqual(p.query, 'up{job="agent"}')
        self.assertEqual(p.threshold, 1.0)
