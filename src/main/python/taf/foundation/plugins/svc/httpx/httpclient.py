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
    def __init__(
            self,
            base_url,
            port=None,
            username=None,
            password=None,
            **kwargs
    ):
        headers = kwargs.pop('headers', None)

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
            verify=False,
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
