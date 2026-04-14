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

from taf.foundation.api.chaos.client import Client, Fault, Probe


class ChaosRunner(Client):
    """High-level chaos experiment orchestrator.

    Usage::

        runner = ChaosRunner(namespace='agentic-platform')

        # Run a full experiment with assertion
        result = runner.assert_resilient(
            fault=PodKill(label_selector='app=agentic-qa-agent'),
            probe=HttpHealthProbe(url='http://agent:8000/health'),
            target='agentic-qa-agent',
            wait_seconds=15,
        )
    """

    def assert_resilient(
            self,
            fault: Fault,
            probe: Probe,
            target: str,
            wait_seconds: float = 10.0,
            retries: int = 3,
            retry_interval: float = 5.0,
            **kwargs
    ) -> dict[str, Any]:
        """Run experiment and assert system remains resilient.

        Retries the probe check up to `retries` times with
        `retry_interval` between attempts (allows recovery time).

        Raises AssertionError if system is not resilient after all retries.
        """
        result: dict[str, Any] = {
            'fault': str(fault),
            'probe': str(probe),
            'target': target,
        }

        try:
            inject_result = self.inject(fault, target, **kwargs)
            result['injected'] = inject_result.get('injected', True)
            result.update(inject_result)

            time.sleep(wait_seconds)

            resilient = False
            for attempt in range(retries):
                resilient = self.verify(probe, target, **kwargs)
                if resilient:
                    break
                if attempt < retries - 1:
                    time.sleep(retry_interval)

            result['resilient'] = resilient
            result['attempts'] = attempt + 1  # type: ignore[possibly-undefined]

        except Exception as ex:
            result['error'] = str(ex)
            result['resilient'] = False
        finally:
            try:
                self.cleanup(fault, target, **kwargs)
                result['cleaned_up'] = True
            except Exception:
                result['cleaned_up'] = False

        if not result.get('resilient'):
            raise AssertionError(
                f"System not resilient after {fault} on {target}.\n"
                f"Result: {result}"
            )

        return result
