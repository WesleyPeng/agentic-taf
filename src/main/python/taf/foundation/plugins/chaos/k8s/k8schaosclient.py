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

from typing import Any

from kubernetes import client, config

from taf.foundation.api.chaos.client import Client, Fault, Probe
from taf.foundation.plugins.chaos.k8s.faults import (
    PodKill, NetworkPartition, FluxSuspend,
)
from taf.foundation.plugins.chaos.k8s.probes import (
    HttpHealthProbe, K8sReadyProbe, PrometheusProbe,
)


class K8sChaosClient(Client):
    """Kubernetes-native chaos client using the kubernetes Python SDK."""

    def __init__(self, namespace: str = 'default', **kwargs):
        super().__init__(namespace, **kwargs)

        kubeconfig = kwargs.get('kubeconfig')
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()

        self._core = client.CoreV1Api()
        self._apps = client.AppsV1Api()
        self._networking = client.NetworkingV1Api()
        self._custom = client.CustomObjectsApi()

    def inject(
            self, fault: Fault, target: str, **kwargs
    ) -> dict[str, Any]:
        ns = kwargs.get('namespace', self.namespace)

        if isinstance(fault, PodKill):
            return self._inject_pod_kill(fault, ns)
        elif isinstance(fault, NetworkPartition):
            return self._inject_network_partition(fault, ns)
        elif isinstance(fault, FluxSuspend):
            return self._inject_flux_suspend(fault, ns)
        else:
            raise ValueError(f'Unsupported fault: {fault}')

    def verify(
            self, probe: Probe, target: str, **kwargs
    ) -> bool:
        ns = kwargs.get('namespace', self.namespace)

        if isinstance(probe, HttpHealthProbe):
            return probe.check()
        elif isinstance(probe, K8sReadyProbe):
            return self._verify_k8s_ready(probe, ns)
        elif isinstance(probe, PrometheusProbe):
            return self._verify_prometheus(probe)
        else:
            raise ValueError(f'Unsupported probe: {probe}')

    def cleanup(
            self, fault: Fault, target: str, **kwargs
    ) -> None:
        ns = kwargs.get('namespace', self.namespace)

        if isinstance(fault, NetworkPartition):
            policy_name = f'chaos-netpol-{fault.label_selector.replace("=", "-")}'
            try:
                self._networking.delete_namespaced_network_policy(
                    policy_name, ns
                )
            except client.ApiException:
                pass
        elif isinstance(fault, FluxSuspend):
            self._resume_flux(fault, ns)

    # --- Fault injection methods ---

    def _inject_pod_kill(
            self, fault: PodKill, namespace: str
    ) -> dict[str, Any]:
        pods = self._core.list_namespaced_pod(
            namespace, label_selector=fault.label_selector
        )
        killed: list[str] = []
        for pod in pods.items[:fault.count]:
            self._core.delete_namespaced_pod(pod.metadata.name, namespace)
            killed.append(pod.metadata.name)

        return {'injected': True, 'killed_pods': killed}

    def _inject_network_partition(
            self, fault: NetworkPartition, namespace: str
    ) -> dict[str, Any]:
        policy_name = f'chaos-netpol-{fault.label_selector.replace("=", "-")}'
        key, value = fault.label_selector.split('=', 1)

        policy = client.V1NetworkPolicy(
            metadata=client.V1ObjectMeta(name=policy_name),
            spec=client.V1NetworkPolicySpec(
                pod_selector=client.V1LabelSelector(
                    match_labels={key: value}
                ),
                policy_types=['Egress'],
                egress=[],
            ),
        )
        self._networking.create_namespaced_network_policy(namespace, policy)
        return {'injected': True, 'policy': policy_name}

    def _inject_flux_suspend(
            self, fault: FluxSuspend, namespace: str
    ) -> dict[str, Any]:
        self._custom.patch_namespaced_custom_object(
            group='kustomize.toolkit.fluxcd.io',
            version='v1',
            namespace=namespace,
            plural='kustomizations',
            name=fault.kustomization_name,
            body={'spec': {'suspend': True}},
        )
        return {'injected': True, 'kustomization': fault.kustomization_name}

    def _resume_flux(self, fault: FluxSuspend, namespace: str) -> None:
        self._custom.patch_namespaced_custom_object(
            group='kustomize.toolkit.fluxcd.io',
            version='v1',
            namespace=namespace,
            plural='kustomizations',
            name=fault.kustomization_name,
            body={'spec': {'suspend': False}},
        )

    # --- Probe verification methods ---

    def _verify_k8s_ready(
            self, probe: K8sReadyProbe, namespace: str
    ) -> bool:
        pods = self._core.list_namespaced_pod(
            namespace, label_selector=probe.label_selector
        )
        ready_count = sum(
            1 for pod in pods.items
            if pod.status and pod.status.phase == 'Running'
            and pod.status.container_statuses
            and all(cs.ready for cs in pod.status.container_statuses)
        )
        return ready_count >= probe.min_ready

    def _verify_prometheus(self, probe: PrometheusProbe) -> bool:
        if not probe.url:
            return False
        try:
            import requests
            resp = requests.get(
                f'{probe.url}/api/v1/query',
                params={'query': probe.query},
                timeout=5,
            )
            data = resp.json()
            results = data.get('data', {}).get('result', [])
            if results:
                value = float(results[0]['value'][1])
                return value >= probe.threshold
        except Exception:
            pass
        return False
