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
