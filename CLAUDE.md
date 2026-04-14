# Agentic-TAF

## Approach

- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files already read unless they may have changed.
- Test code before declaring done. Run relevant lint/typecheck/test after every change.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct.
- User instructions always override this file.

## Project

Agentic Test Automation Framework — an extensible, plugin-based, multi-layered
Python framework for test automation across API, Web UI, WebSocket, CLI,
AI/LLM validation, and chaos engineering. Evolved from uiXautomation (PyXTaf),
modernized for Python 3.12+.

Part of the Agentic QA Platform (6 repos). Design authority and implementation
plans live in `agentic-qa-platform`. This repo contains the framework core and
platform test suites (eat your own dogfood).

Language: Python 3.12+

## Architecture

Four-layer plugin architecture (top to bottom):

1. **Test Suites** (`src/test/python/`) — `ut/` (142 unit tests), `suites/agentic/` (50 E2E: 21 API + 8 security + 10 UI + 11 AI), `bpt/` (BDD/ATDD examples)
2. **Modeling** (`src/main/python/taf/modeling/`) — Browser, RESTClient, CLIRunner, WSClient, LLMJudge, ChaosRunner
3. **Foundation** (`src/main/python/taf/foundation/`) — ServiceLocator, Configuration (YAML), Utils
4. **Plugins** (`src/main/python/taf/foundation/plugins/`) — Concrete implementations discovered at runtime via ServiceLocator

Plugin interfaces in `taf/foundation/api/plugins/`:

| Interface | Implementation | Status |
|-----------|----------------|--------|
| `WebPlugin` | `SeleniumPlugin` (default, headless) | Implemented |
| `WebPlugin` | `PlaywrightPlugin` (optional) | Implemented (T.1.3) |
| `RESTPlugin` | `RequestsPlugin` (default) | Implemented |
| `RESTPlugin` | `HttpxRESTPlugin` (optional) | Implemented (T.1.3) |
| `WSPlugin` | `WebSocketPlugin` (optional) | Implemented (T.1.3) |
| `CLIPlugin` | `ParamikoPlugin` | Implemented |
| `MobilePlugin` | `AppiumPlugin` | Implemented |
| `LLMPlugin` | `LLMJudgePlugin` (optional, OpenAI/Anthropic) | Implemented (T.1.3+T.1.4) |
| `ChaosPlugin` | `K8sChaosPlugin` (optional) | Implemented (T.1.5) |

## Build & Test

```bash
# Lint
flake8 src/main/python/ src/test/python/ --max-line-length=120

# Type check
mypy src/main/python/taf/ --ignore-missing-imports

# Framework unit tests (142 tests)
PYTHONPATH=src/main/python pytest src/test/python/ut/ -v
```

## Conventions

- **Files/dirs**: lowercase-with-hyphens for directories, lowercase_with_underscores for Python modules.
- **Plugins**: One plugin class per file. File named `<name>plugin.py` (e.g., `playwrightplugin.py`).
- **Plugin interfaces**: Abstract base in `taf/foundation/api/plugins/`. Concrete in `taf/foundation/plugins/<type>/<name>/`.
- **Modeling**: High-level wrappers in `taf/modeling/<type>/`. Must use ServiceLocator to resolve plugins, never import concrete plugins directly.
- **Config**: YAML files in `taf/foundation/conf/` (framework). Environment variables override YAML values (`TAF_PLUGIN_<NAME>_<KEY>`, `TAF_LLM_PROVIDER`).
- **Commits**: `<scope>: <description>` — scopes: framework, plugin, modeling, test, ci, docs.
- **Copyright**: `Copyright (c) 2017-2026 Wesley Peng` — LGPL-3.0 license.
- **No secrets**: Never hardcode credentials, IPs, or tokens. Use config files or env vars.

## Key Patterns

### ServiceLocator (plugin discovery)

```python
from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import WebPlugin, RESTPlugin

# Resolves concrete plugin based on config.yml
Browser = ServiceLocator.get_app_under_test(WebPlugin)
client = ServiceLocator.get_client(RESTPlugin)
```

### Adding a new plugin

1. Create interface in `taf/foundation/api/plugins/<name>plugin.py` (extend `BasePlugin` metaclass)
2. Create base client in `taf/foundation/api/<type>/client.py`
3. Create concrete implementation in `taf/foundation/plugins/<type>/<name>/`
4. Register in `taf/foundation/conf/config.yml`
5. Add modeling wrapper in `taf/modeling/<type>/` if needed
6. Write unit test in `src/test/python/ut/`

## Pitfalls

- **Never import concrete plugins in test code** — always go through ServiceLocator or modeling layer. Direct imports break plugin swappability.
- **ServiceLocator is a singleton** — plugin resolution happens once per type. Configuration must be set before first access.
- **config.yml `location` is relative** — plugin paths are relative to `taf/foundation/conf/`. Use `../plugins/...` pattern.
- **Selenium 4 API** — use `find_elements(By.ID, value)` not deprecated `find_elements_by_id()`. Use `Service` and `Options`, not `executable_path` or `desired_capabilities`.
- **LLM provider selection** — default is `openai` (OpenAI-compatible). Set `TAF_LLM_PROVIDER=anthropic` or pass `provider='anthropic'` for native Anthropic API.
- **Optional plugins** — websocket, llm, chaos plugins are `enabled: False` by default. Install the optional dep (`pip install .[chaos]`) and set `enabled: True` or use env var override.
- **Configuration env overrides are case-insensitive** — `TAF_PLUGIN_REST_NAME` matches config key `REST` (uppercase). The lookup normalizes to lowercase.
- **E2E tests use ServiceLocator** — never import `httpx.Client` or concrete plugins directly. Use `conftest.py` fixtures that resolve via `ServiceLocator.get_client(RESTPlugin)` with env override.
- **BDD tests use behave, not pytest-bdd** — existing examples in `src/test/python/bpt/bdd/` use behave with Gherkin.
