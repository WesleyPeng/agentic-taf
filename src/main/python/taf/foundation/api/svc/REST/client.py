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
        # Delegate to close() so subclasses release transport resources
        # (httpx.Client, requests.Session, etc.) via a single hook. The
        # base implementation of close() is a no-op so a bare Client used
        # as a context manager doesn't crash — overriding __exit__ to
        # raise NotImplementedError violated LSP and broke every `with`
        # block consuming a Client subclass that didn't override __exit__.
        self.close()

    def close(self) -> None:
        """Release transport resources. Default is a no-op; subclasses
        with a live HTTP client (httpx.Client, requests.Session, etc.)
        should override to call the underlying client's close method."""

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
