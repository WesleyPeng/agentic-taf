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
