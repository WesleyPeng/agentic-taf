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
