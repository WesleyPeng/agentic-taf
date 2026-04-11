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

from taf.foundation.api.llm import Client


class LLMJudge(Client):
    """High-level LLM-as-judge evaluator with threshold assertions.

    Supports both OpenAI-compatible and Anthropic providers::

        # OpenAI-compatible (default) — works with local LLMs, OpenRouter
        judge = LLMJudge(
            model='gpt-4o-mini',
            provider='openai',
            base_url='http://localhost:11434/v1',  # e.g. Ollama
        )

        # Anthropic
        judge = LLMJudge(
            model='claude-sonnet-4-20250514',
            provider='anthropic',
        )

        # Evaluate with threshold
        result = judge.assert_quality(
            prompt='What environments are running?',
            response='Currently there are 3 active environments...',
            context={'actual_count': 3},
            overall_threshold=3.5,
            dimension_thresholds={'accuracy': 4.0},
        )
    """

    def assert_quality(
            self,
            prompt: str,
            response: str,
            context: dict | None = None,
            overall_threshold: float = 3.5,
            dimension_thresholds: dict[str, float] | None = None,
            fail_any_below: float | None = 2.0,
    ) -> dict:
        """Evaluate and raise AssertionError if thresholds not met.

        Args:
            prompt: The user prompt that was sent
            response: The AI response to evaluate
            context: Ground truth data for comparison
            overall_threshold: Minimum overall score (default 3.5)
            dimension_thresholds: Per-dimension minimum scores
            fail_any_below: Fail if ANY dimension scores below this

        Returns:
            dict with dimension scores + 'overall' + 'passed' bool

        Raises:
            AssertionError with details if thresholds not met
        """
        scores = self.evaluate(prompt, response, context=context)
        failures: list[str] = []

        if scores['overall'] < overall_threshold:
            failures.append(
                f"overall {scores['overall']:.2f} < {overall_threshold}"
            )

        if fail_any_below is not None:
            for dim, val in scores.items():
                if dim != 'overall' and val < fail_any_below:
                    failures.append(
                        f"{dim} {val:.2f} < {fail_any_below} (floor)"
                    )

        if dimension_thresholds:
            for dim, threshold in dimension_thresholds.items():
                if dim in scores and scores[dim] < threshold:
                    failures.append(
                        f"{dim} {scores[dim]:.2f} < {threshold}"
                    )

        scores['passed'] = len(failures) == 0

        if failures:
            raise AssertionError(
                f"LLM quality check failed: {'; '.join(failures)}\n"
                f"Scores: {scores}"
            )

        return scores
