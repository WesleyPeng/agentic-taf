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

"""AI suite fixtures.

The actual ``llm_judge`` and ``llm_client_cls`` fixtures were promoted
to the shared ``suites/agentic/conftest.py`` in T.10.2 so that non-AI
suites (chaos, security, BDD) can opt in via ``llm_judge_optional`` and
``chat_and_judge``. The AI suite continues to use the required ``llm_judge``
fixture which skips the test if langchain is unavailable — that behaviour
is preserved by the shared fixture's contract.

This file is intentionally minimal so AI-specific fixtures can be added
in the future without disturbing the shared layer.
"""
