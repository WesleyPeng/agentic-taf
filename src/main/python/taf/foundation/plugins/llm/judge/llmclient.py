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
import os
from typing import Any

from taf.foundation.api.llm import Client


def _create_chat_model(
        provider: str,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs
) -> Any:
    """Create a LangChain chat model based on provider.

    Supports:
      - 'openai': langchain-openai ChatOpenAI (also works with
        OpenAI-compatible APIs like local LLMs, OpenRouter, vLLM)
      - 'anthropic': langchain-anthropic ChatAnthropic
    """
    if provider == Client.PROVIDER_ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        init_kwargs: dict[str, Any] = {
            'model_name': model,
            'temperature': kwargs.get('temperature', 0.0),
        }
        if api_key:
            init_kwargs['anthropic_api_key'] = api_key
        return ChatAnthropic(**init_kwargs)

    # Default: OpenAI-compatible (works with OpenAI, OpenRouter,
    # local LLMs, vLLM, etc.)
    from langchain_openai import ChatOpenAI
    init_kwargs = {
        'model': model,
        'temperature': kwargs.get('temperature', 0.0),
        'max_tokens': kwargs.get('max_tokens', 1024),
    }
    if base_url:
        init_kwargs['base_url'] = base_url
    if api_key:
        init_kwargs['api_key'] = api_key
    return ChatOpenAI(**init_kwargs)


class LLMClient(Client):
    DEFAULT_MODELS = {
        Client.PROVIDER_OPENAI: 'gpt-4o-mini',
        Client.PROVIDER_ANTHROPIC: 'claude-sonnet-4-20250514',
    }

    def __init__(
            self,
            model: str | None = None,
            rubric: dict[str, str] | None = None,
            provider: str | None = None,
            base_url: str | None = None,
            api_key: str | None = None,
            **kwargs
    ):
        _provider = (
            provider
            or os.environ.get('TAF_LLM_PROVIDER', Client.PROVIDER_OPENAI)
        )
        _model = model or self.DEFAULT_MODELS.get(
            _provider, 'gpt-4o-mini'
        )

        super().__init__(
            _model, rubric,
            provider=_provider,
            base_url=base_url,
            api_key=api_key,
            **kwargs
        )

        self._llm = _create_chat_model(
            self.provider, self.model or _model,
            base_url=self.base_url,
            api_key=self.api_key,
            **kwargs
        )

    def evaluate(
            self,
            prompt: str,
            response: str,
            context: dict | None = None,
            **kwargs
    ) -> dict:
        scores: dict[str, float] = {}
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
