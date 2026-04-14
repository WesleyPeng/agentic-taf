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

from unittest import TestCase
from unittest.mock import MagicMock, patch

from taf.foundation.api.chaos.client import Fault, Probe
from taf.modeling.chaos.chaosrunner import ChaosRunner


class TestChaosRunner(TestCase):
    """Tests for ChaosRunner modeling layer."""

    def test_assert_resilient_passes(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(return_value={'injected': True})
        runner.verify = MagicMock(return_value=True)
        runner.cleanup = MagicMock()

        with patch('taf.modeling.chaos.chaosrunner.time.sleep'):
            result = runner.assert_resilient(
                fault=Fault('test_fault'),
                probe=Probe('test_probe'),
                target='agent',
                wait_seconds=0,
            )

        self.assertTrue(result['resilient'])
        self.assertTrue(result['cleaned_up'])
        runner.cleanup.assert_called_once()

    def test_assert_resilient_fails(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(return_value={'injected': True})
        runner.verify = MagicMock(return_value=False)
        runner.cleanup = MagicMock()

        with patch('taf.modeling.chaos.chaosrunner.time.sleep'):
            with self.assertRaises(AssertionError) as ctx:
                runner.assert_resilient(
                    fault=Fault('test_fault'),
                    probe=Probe('test_probe'),
                    target='agent',
                    wait_seconds=0,
                    retries=1,
                )
            self.assertIn('not resilient', str(ctx.exception))

    def test_assert_resilient_retries(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(return_value={'injected': True})
        runner.verify = MagicMock(side_effect=[False, False, True])
        runner.cleanup = MagicMock()

        with patch('taf.modeling.chaos.chaosrunner.time.sleep'):
            result = runner.assert_resilient(
                fault=Fault('test_fault'),
                probe=Probe('test_probe'),
                target='agent',
                wait_seconds=0,
                retries=3,
                retry_interval=0,
            )

        self.assertTrue(result['resilient'])
        self.assertEqual(result['attempts'], 3)
        self.assertEqual(runner.verify.call_count, 3)

    def test_assert_resilient_cleanup_on_failure(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(return_value={'injected': True})
        runner.verify = MagicMock(return_value=False)
        runner.cleanup = MagicMock()

        with patch('taf.modeling.chaos.chaosrunner.time.sleep'):
            with self.assertRaises(AssertionError):
                runner.assert_resilient(
                    fault=Fault('f'), probe=Probe('p'),
                    target='t', wait_seconds=0, retries=1,
                )

        runner.cleanup.assert_called_once()

    def test_assert_resilient_inject_error(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(side_effect=RuntimeError('K8s unreachable'))
        runner.cleanup = MagicMock()

        with patch('taf.modeling.chaos.chaosrunner.time.sleep'):
            with self.assertRaises(AssertionError) as ctx:
                runner.assert_resilient(
                    fault=Fault('f'), probe=Probe('p'),
                    target='t', wait_seconds=0, retries=1,
                )
            self.assertIn('K8s unreachable', str(ctx.exception))

    def test_run_experiment_full_lifecycle(self):
        runner = ChaosRunner(namespace='test')
        runner.inject = MagicMock(return_value={'injected': True})
        runner.verify = MagicMock(return_value=True)
        runner.cleanup = MagicMock()

        with patch('taf.foundation.api.chaos.client.time.sleep'):
            result = runner.run_experiment(
                fault=Fault('f'), probe=Probe('p'),
                target='t', wait_seconds=0,
            )

        self.assertTrue(result['resilient'])
        self.assertTrue(result['cleaned_up'])
