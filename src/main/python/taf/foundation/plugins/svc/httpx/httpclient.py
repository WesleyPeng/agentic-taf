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

import httpx

from taf.foundation.api.svc.REST import Client


class HttpClient(Client):
    """httpx-backed REST client for the test automation framework.

    TLS verification defaults to ``False`` because Agentic-TAF targets
    test environments that frequently use self-signed certificates
    (preprod kubeadm clusters, in-cluster service URLs, lab vCenters).
    Production-grade callers can override by passing ``verify=`` to the
    constructor:

        HttpClient(url, verify=True)                  # system trust store
        HttpClient(url, verify='/path/to/ca.pem')     # custom CA bundle
        HttpClient(url, verify=False)                 # explicit (default)

    See ``docs/architecture.md`` and the platform's
    ``docs/07-security-access-control.md`` for guidance on production usage.
    """

    def __init__(
            self,
            base_url,
            port=None,
            username=None,
            password=None,
            **kwargs
    ):
        headers = kwargs.pop('headers', None)
        # Caller may override TLS verification; preserve test-friendly default.
        verify = kwargs.pop('verify', False)

        super().__init__(
            base_url, port,
            username, password, **kwargs
        )

        auth = None
        if username:
            auth = httpx.BasicAuth(username, password or '')

        self._client = httpx.Client(
            base_url=self.params.get('url', ''),
            auth=auth,
            headers=headers,
            verify=verify,
            timeout=kwargs.get('timeout', 60.0),
        )

    def __exit__(self, *args):
        self._client.close()

    def get(self, resource, **kwargs):
        return self._client.get(
            resource,
            **self._set_default_timeout(**kwargs)
        )

    def post(self, resource, data=None, **kwargs):
        json_data = kwargs.pop('json', None)
        return self._client.post(
            resource,
            content=data,
            json=json_data,
            **self._set_default_timeout(**kwargs)
        )

    def put(self, resource, data=None, **kwargs):
        return self._client.put(
            resource,
            content=data,
            **self._set_default_timeout(**kwargs)
        )

    def delete(self, resource, **kwargs):
        return self._client.delete(
            resource,
            **self._set_default_timeout(**kwargs)
        )

    def patch(self, resource, data=None, **kwargs):
        return self._client.patch(
            resource,
            content=data,
            **self._set_default_timeout(**kwargs)
        )

    def _set_default_timeout(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.params.get('timeout', 60)
        return kwargs
