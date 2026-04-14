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

from taf.foundation.api.chaos.client import Fault


class PodKill(Fault):
    """Kill one or more pods matching a label selector."""

    def __init__(self, label_selector: str, count: int = 1):
        super().__init__('pod_kill', label_selector=label_selector, count=count)
        self.label_selector = label_selector
        self.count = count


class NetworkPartition(Fault):
    """Block network traffic to/from target pods."""

    def __init__(self, label_selector: str, block_cidr: str = '0.0.0.0/0'):
        super().__init__(
            'network_partition',
            label_selector=label_selector, block_cidr=block_cidr,
        )
        self.label_selector = label_selector
        self.block_cidr = block_cidr


class ResourcePressure(Fault):
    """Apply resource limits (CPU/memory) to target pods."""

    def __init__(self, label_selector: str, cpu: str = '50m', memory: str = '64Mi'):
        super().__init__(
            'resource_pressure',
            label_selector=label_selector, cpu=cpu, memory=memory,
        )
        self.label_selector = label_selector
        self.cpu = cpu
        self.memory = memory


class DNSFailure(Fault):
    """Corrupt DNS resolution for a target service."""

    def __init__(self, service_name: str):
        super().__init__('dns_failure', service_name=service_name)
        self.service_name = service_name


class FluxSuspend(Fault):
    """Suspend a Flux Kustomization to simulate GitOps stall."""

    def __init__(self, kustomization_name: str):
        super().__init__('flux_suspend', kustomization_name=kustomization_name)
        self.kustomization_name = kustomization_name
