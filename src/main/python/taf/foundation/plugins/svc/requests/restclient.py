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


class RESTClient(Session, Client):
    def __init__(
            self,
            base_url,
            port=None,
            username=None,
            password=None,
            **kwargs
    ):
        Session.__init__(self)

        Client.__init__(
            self, base_url, port,
            username, password, **kwargs
        )

        self.verify = False

        self._set_auth(
            username, password
        )

        urllib3.disable_warnings()

    def get(self, url, **kwargs):
        return Session.get(
            self,
            self._get_resource_uri(url),
            **self._set_default_timeout(
                **kwargs
            )
        )

    def post(
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

    def put(self, url, data=None, **kwargs):
        return Session.put(
            self,
            self._get_resource_uri(url),
            data,
            **self._set_default_timeout(
                **kwargs
            )
        )

    def delete(self, url, **kwargs):
        return Session.delete(
            self,
            self._get_resource_uri(url),
            **self._set_default_timeout(
                **kwargs
            )
        )

    def patch(self, url, data=None, **kwargs):
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

    def _get_resource_uri(self, resource):
        import sys

        if sys.version_info.major < 3:
            from urlparse import urljoin
        else:
            from urllib.parse import urljoin

        return urljoin(
            self.params.get('url'),
            resource
        )

    def _set_default_timeout(self, **kwargs):
        kwargs.setdefault(
            'timeout',
            self.params.get('timeout', 60)
        )

        return kwargs
