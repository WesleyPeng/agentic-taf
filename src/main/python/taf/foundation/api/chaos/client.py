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

import time
from typing import Any


class Fault:
    """Base class for fault definitions."""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.params = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'


class Probe:
    """Base class for resilience probes."""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.params = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'


class Client:
    """Base chaos client — inject faults, verify resilience, run experiments."""

    def __init__(self, namespace: str = 'default', **kwargs):
        self.namespace = namespace
        self.params = kwargs

    def inject(
            self,
            fault: Fault,
            target: str,
            **kwargs
    ) -> dict[str, Any]:
        """Inject a fault into the target.

        Returns dict with 'injected': True/False and fault details.
        """
        raise NotImplementedError('Inject fault')

    def verify(
            self,
            probe: Probe,
            target: str,
            **kwargs
    ) -> bool:
        """Run a resilience probe against the target.

        Returns True if the system is healthy/resilient.
        """
        raise NotImplementedError('Verify resilience')

    def cleanup(
            self,
            fault: Fault,
            target: str,
            **kwargs
    ) -> None:
        """Revert an injected fault."""
        raise NotImplementedError('Cleanup fault')

    def run_experiment(
            self,
            fault: Fault,
            probe: Probe,
            target: str,
            wait_seconds: float = 10.0,
            **kwargs
    ) -> dict[str, Any]:
        """Full chaos experiment lifecycle.

        1. Inject fault
        2. Wait for propagation
        3. Verify resilience via probe
        4. Cleanup fault
        5. Return result dict
        """
        result: dict[str, Any] = {
            'fault': str(fault),
            'probe': str(probe),
            'target': target,
        }

        try:
            inject_result = self.inject(fault, target, **kwargs)
            result['injected'] = inject_result.get('injected', True)

            time.sleep(wait_seconds)

            result['resilient'] = self.verify(probe, target, **kwargs)
        except Exception as ex:
            result['error'] = str(ex)
            result['resilient'] = False
        finally:
            try:
                self.cleanup(fault, target, **kwargs)
                result['cleaned_up'] = True
            except Exception:
                result['cleaned_up'] = False

        return result
