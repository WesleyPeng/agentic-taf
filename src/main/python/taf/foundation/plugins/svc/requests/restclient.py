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

import urllib3
from requests.auth import HTTPBasicAuth
from requests.sessions import Session

from taf.foundation.api.svc.REST import Client


class RESTClient(Session, Client):  # type: ignore[misc]
    """requests-backed REST client for the test automation framework.

    TLS verification defaults to ``False`` because Agentic-TAF targets
    test environments that frequently use self-signed certificates
    (preprod kubeadm clusters, in-cluster service URLs, lab vCenters).
    Production-grade callers can override by passing ``verify=`` to the
    constructor:

        RESTClient(url, verify=True)                # system trust store
        RESTClient(url, verify='/path/to/ca.pem')   # custom CA bundle
        RESTClient(url, verify=False)               # explicit (default)

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
        Session.__init__(self)

        # Caller may override TLS verification; preserve test-friendly default.
        verify = kwargs.pop('verify', False)

        Client.__init__(
            self, base_url, port,
            username, password, **kwargs
        )

        self.verify = verify

        self._set_auth(
            username, password
        )

        # Only suppress warnings when verification is intentionally
        # disabled — caller opting in to verification deserves the
        # default warning behaviour.
        if verify is False:
            urllib3.disable_warnings()

    def get(self, url, **kwargs):  # type: ignore[override]
        return Session.get(
            self,
            self._get_resource_uri(url),
            **self._set_default_timeout(
                **kwargs
            )
        )

    def post(  # type: ignore[override]
            self,
            url,
            data=None,
            json=None,
            **kwargs
    ):
        return Session.post(
            self,
            self._get_resource_uri(url),
            data, json,
            **self._set_default_timeout(
                **kwargs
            )
        )

    def put(self, url, data=None, **kwargs):  # type: ignore[override]
        return Session.put(
            self,
            self._get_resource_uri(url),
            data,
            **self._set_default_timeout(
                **kwargs
            )
        )

    def delete(self, url, **kwargs):  # type: ignore[override]
        return Session.delete(
            self,
            self._get_resource_uri(url),
            **self._set_default_timeout(
                **kwargs
            )
        )

    def patch(self, url, data=None, **kwargs):  # type: ignore[override]
        return Session.patch(
            self,
            self._get_resource_uri(url),
            data,
            **self._set_default_timeout(
                **kwargs
            )
        )

    def _set_auth(
            self,
            username,
            password
    ):
        self.auth = HTTPBasicAuth(
            username,
            password
        )

    def _get_resource_uri(self, resource: str) -> str:
        from urllib.parse import urljoin

        return urljoin(
            self.params.get('url'),  # type: ignore[union-attr]
            resource
        )

    def _set_default_timeout(self, **kwargs):
        kwargs.setdefault(
            'timeout',
            self.params.get('timeout', 60)  # type: ignore[union-attr]
        )

        return kwargs
