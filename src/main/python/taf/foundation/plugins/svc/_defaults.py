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

"""Shared defaults mixin for REST client plugins.

The httpx- and requests-backed clients had near-identical
``_set_default_timeout`` implementations. Extracted here so they stay
in sync — both call sites now derive from this single source.

Kept TLS-verify-default constants here too as documentation: the
actual ``verify=`` default lives in each client's ``__init__`` because
the call signatures differ slightly, but the value is centralized.
"""

from typing import Any

# Default values shared by REST client plugins. Centralized so a
# security-posture change (e.g. tightening default timeout) updates
# both clients atomically.
DEFAULT_TIMEOUT_SECONDS: float = 60.0
DEFAULT_VERIFY_TLS: bool = True


class RestClientDefaults:
    """Mixin: shared timeout-defaulting behavior for REST client plugins.

    Both :class:`HttpClient` (httpx) and :class:`RESTClient` (requests)
    expose ``self.params`` (a dict populated by the base ``Client``
    constructor) and need to default a ``timeout`` kwarg on every HTTP
    verb call. This mixin centralizes the lookup precedence:

      1. explicit ``timeout=`` from the caller (left untouched)
      2. otherwise: ``self.params['timeout']``
      3. otherwise: ``DEFAULT_TIMEOUT_SECONDS``
    """

    params: dict[str, Any]  # provided by base Client

    def _set_default_timeout(self, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault(
            'timeout',
            self.params.get('timeout', DEFAULT_TIMEOUT_SECONDS),
        )
        return kwargs
