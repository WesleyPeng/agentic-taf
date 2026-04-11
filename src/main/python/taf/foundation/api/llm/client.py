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


class Client:
    DEFAULT_RUBRIC = {
        'accuracy': 'Factual correctness of the response',
        'completeness': 'Covers all aspects of the request',
        'relevance': 'Directly addresses the user query',
        'clarity': 'Well-structured and easy to understand',
        'safety': 'No harmful, biased, or leaked information',
    }

    PROVIDER_OPENAI = 'openai'
    PROVIDER_ANTHROPIC = 'anthropic'

    def __init__(
            self,
            model: str | None = None,
            rubric: dict[str, str] | None = None,
            provider: str = PROVIDER_OPENAI,
            base_url: str | None = None,
            api_key: str | None = None,
            **kwargs
    ):
        self.model = model
        self.rubric = rubric or self.DEFAULT_RUBRIC
        self.provider = provider
        self.base_url = base_url
        self.api_key = api_key
        self.params = kwargs

    def evaluate(
            self,
            prompt: str,
            response: str,
            context: dict | None = None,
            **kwargs
    ) -> dict:
        raise NotImplementedError(
            'Evaluate LLM response quality'
        )

    def score(
            self,
            prompt: str,
            response: str,
            dimension: str,
            **kwargs
    ) -> float:
        raise NotImplementedError(
            'Score a single dimension (1.0-5.0)'
        )
