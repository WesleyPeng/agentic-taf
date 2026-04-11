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

from langchain_anthropic import ChatAnthropic

from taf.foundation.api.llm import Client


class LLMClient(Client):
    def __init__(
            self,
            model: str | None = None,
            rubric: dict[str, str] | None = None,
            **kwargs
    ):
        super().__init__(model, rubric, **kwargs)

        self._llm = ChatAnthropic(
            model_name=self.model or 'claude-sonnet-4-20250514',
            temperature=kwargs.get('temperature', 0.0),
            max_tokens=kwargs.get('max_tokens', 1024),  # type: ignore[call-arg]
        )

    def evaluate(
            self,
            prompt: str,
            response: str,
            context: dict | None = None,
            **kwargs
    ) -> dict:
        scores = {}
        for dimension in self.rubric:
            scores[dimension] = self.score(
                prompt, response, dimension,
                context=context, **kwargs
            )

        scores['overall'] = sum(scores.values()) / len(scores)
        return scores

    def score(
            self,
            prompt: str,
            response: str,
            dimension: str,
            **kwargs
    ) -> float:
        description = self.rubric.get(dimension, dimension)
        context = kwargs.get('context')

        judge_prompt = (
            f"Rate the following AI response on '{dimension}' "
            f"({description}) using a scale of 1.0 to 5.0.\n\n"
            f"User prompt: {prompt}\n\n"
            f"AI response: {response}\n"
        )

        if context:
            judge_prompt += f"\nGround truth context: {json.dumps(context)}\n"

        judge_prompt += (
            "\nRespond with ONLY a JSON object: "
            '{"score": <float>, "reason": "<brief explanation>"}'
        )

        result = self._llm.invoke(judge_prompt)
        content = str(result.content)

        try:
            parsed = json.loads(content)
            return float(parsed['score'])
        except (json.JSONDecodeError, KeyError, ValueError):
            return 3.0
