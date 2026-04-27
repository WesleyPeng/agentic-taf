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
from typing import Any, Callable

from taf.foundation.api.llm import Client


# --- Provider registry (OCP-compliant factory) -------------------------------
#
# Each provider is a callable ``(model, base_url, api_key, **kwargs) -> Any``
# that returns a LangChain chat model instance. Register new providers via
# ``register_provider()`` instead of editing this file — adding a new provider
# does not require modifying ``_create_chat_model`` (Open/Closed Principle).
#
# Lazy imports inside each builder keep optional SDK dependencies optional:
# only the provider actually requested is imported at runtime.

_ProviderBuilder = Callable[..., Any]
_PROVIDER_REGISTRY: dict[str, _ProviderBuilder] = {}


def register_provider(name: str, builder: _ProviderBuilder) -> None:
    """Register a new chat-model provider.

    Args:
        name: Provider identifier (e.g., ``'openai'``, ``'anthropic'``,
            ``'ollama'``). Should match the value used in
            ``Client.PROVIDER_*`` constants or the ``TAF_LLM_PROVIDER``
            environment variable.
        builder: Callable with signature
            ``(model, base_url, api_key, **kwargs) -> BaseChatModel``.
    """
    _PROVIDER_REGISTRY[name] = builder


def _build_openai(
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs
) -> Any:
    """OpenAI-compatible chat model (OpenAI, OpenRouter, Ollama, vLLM, ...)."""
    from langchain_openai import ChatOpenAI
    init_kwargs: dict[str, Any] = {
        'model': model,
        'temperature': kwargs.get('temperature', 0.0),
        'max_tokens': kwargs.get('max_tokens', 1024),
    }
    if base_url:
        init_kwargs['base_url'] = base_url
    if api_key:
        init_kwargs['api_key'] = api_key
    return ChatOpenAI(**init_kwargs)


def _build_anthropic(
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs
) -> Any:
    """Anthropic Claude chat model (native Messages API, not OpenAI-compat)."""
    from langchain_anthropic import ChatAnthropic
    init_kwargs: dict[str, Any] = {
        'model_name': model,
        'temperature': kwargs.get('temperature', 0.0),
    }
    if api_key:
        init_kwargs['anthropic_api_key'] = api_key
    return ChatAnthropic(**init_kwargs)


# Register the two built-in providers. New providers can be added at runtime
# (e.g., from a plugin) by calling ``register_provider()`` without modifying
# this module — that's the OCP win.
register_provider(Client.PROVIDER_OPENAI, _build_openai)
register_provider(Client.PROVIDER_ANTHROPIC, _build_anthropic)


def _create_chat_model(
        provider: str,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs
) -> Any:
    """Create a LangChain chat model for the named provider.

    Falls back to the OpenAI-compatible builder when the provider is not
    registered, preserving the prior default behaviour.
    """
    builder = _PROVIDER_REGISTRY.get(provider, _build_openai)
    return builder(
        model,
        base_url=base_url,
        api_key=api_key,
        **kwargs,
    )


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
