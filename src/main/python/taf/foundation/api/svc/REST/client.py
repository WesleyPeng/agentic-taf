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

import json
from urllib.parse import urlparse

from taf.foundation.utils import YAMLData


class Client:
    def __init__(
            self,
            base_url: str,
            port: int | None = None,
            username: str | None = None,
            password: str | None = None,
            **kwargs
    ):

        _url = urlparse(base_url)

        if port and str(port).strip():
            assert str(port).strip().isdigit(), \
                'Invalid port number'

            _url._replace(
                netloc='{}:{}'.format(
                    _url.hostname,
                    str(port).strip()
                )
            )

        kwargs.update(
            url=_url.geturl(),
            username=username,
            password=password
        )

        self.params = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args):
        raise NotImplementedError(
            'Close connection'
        )

    def get(
            self,
            resource,
            **kwargs
    ):
        raise NotImplementedError(
            'GET - To retrieve a resource'
        )

    def post(
            self,
            resource,
            data=None,
            **kwargs
    ):
        raise NotImplementedError(
            'POST - To create a resource,'
            'or to execute a complex operation on a resource'
        )

    def put(
            self,
            resource,
            data=None,
            **kwargs
    ):
        raise NotImplementedError(
            'PUT - To update a resource'
        )

    def delete(
            self,
            resource,
            **kwargs
    ):
        raise NotImplementedError(
            'DELETE - To delete a resource'
        )

    def patch(
            self,
            resource,
            data=None,
            **kwargs
    ):
        raise NotImplementedError(
            'PATCH - To perform a partial update to a resource'
        )

    @classmethod
    def decode(cls, json_string: str) -> YAMLData | list | dict:
        try:
            parsed = json.loads(json_string)

            if isinstance(parsed, dict):
                return YAMLData(**parsed)
            else:
                return parsed
        except (TypeError, ValueError):
            return {}

    @classmethod
    def encode(cls, model: object) -> str:
        def _iter_encode(data: object) -> object:
            if isinstance(data, YAMLData):
                data = vars(data)

            if isinstance(data, dict):
                return {key: _iter_encode(value) for key, value in data.items()}
            elif isinstance(data, (list, tuple)):
                return [_iter_encode(item) for item in data]
            else:
                return data

        return json.dumps(
            _iter_encode(model),
            indent=2,
            sort_keys=True
        )
