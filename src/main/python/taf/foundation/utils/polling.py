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

"""Simple polling utility shared by UI / API / chaos plugins.

Replaces hand-rolled `while not condition: sleep(1)` loops scattered
across the framework. Caller passes a predicate (callable returning
truthy when the wait can end) and gets back True if the condition
became true, False if timeout elapsed first.
"""

import time
from typing import Callable


def poll_until(
    predicate: Callable[[], object],
    timeout: float = 30.0,
    interval: float = 1.0,
) -> bool:
    """Block until ``predicate()`` returns truthy or ``timeout`` elapses.

    Args:
        predicate: Zero-arg callable polled on each iteration.
        timeout: Max seconds to wait. Default 30.
        interval: Seconds between polls. Default 1.

    Returns:
        True if ``predicate()`` returned truthy within the timeout,
        False otherwise.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    # Final check after loop exit (avoids racing the deadline boundary).
    return bool(predicate())
