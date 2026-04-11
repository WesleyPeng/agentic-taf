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
    """High-level LLM-as-judge evaluator.

    Usage via ServiceLocator when LLMPlugin is enabled in config,
    or directly for standalone LLM testing:

        judge = LLMJudge(model='claude-sonnet-4-20250514')
        scores = judge.evaluate(
            prompt='What environments are running?',
            response='Currently there are 3 active environments...',
            context={'actual_count': 3}
        )
        assert scores['accuracy'] >= 4.0
    """
    pass
