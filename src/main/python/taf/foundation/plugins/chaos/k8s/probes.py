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

import requests

from taf.foundation.api.chaos.client import Probe


class HttpHealthProbe(Probe):
    """Check HTTP health endpoint."""

    def __init__(self, url: str, expected_status: int = 200, timeout: float = 5.0):
        super().__init__('http_health', url=url, expected_status=expected_status)
        self.url = url
        self.expected_status = expected_status
        self.timeout = timeout

    def check(self) -> bool:
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            return resp.status_code == self.expected_status
        except Exception:
            return False


class K8sReadyProbe(Probe):
    """Check that K8s pods matching a selector are Ready."""

    def __init__(self, label_selector: str, min_ready: int = 1):
        super().__init__(
            'k8s_ready',
            label_selector=label_selector, min_ready=min_ready,
        )
        self.label_selector = label_selector
        self.min_ready = min_ready


class PrometheusProbe(Probe):
    """Query Prometheus and assert metric value."""

    def __init__(self, query: str, threshold: float = 0.0, url: str = ''):
        super().__init__(
            'prometheus_query',
            query=query, threshold=threshold, url=url,
        )
        self.query = query
        self.threshold = threshold
        self.url = url
