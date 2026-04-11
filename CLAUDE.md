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
Python framework for test automation across API, Web UI, WebSocket, CLI, and
AI/LLM validation. Evolved from uiXautomation (PyXTaf), modernized for Python 3.12+.

Part of the Agentic QA Platform (6 repos). Design authority and implementation
plans live in `agentic-qa-platform`. This repo contains the framework core and
platform test suites (eat your own dogfood).

Language: Python 3.12+

## Architecture

Four-layer plugin architecture (top to bottom):

1. **Test Suites** (`src/test/python/`) — `ut/` (42 unit tests), `bpt/` (BDD/ATDD examples), `suites/` (planned)
2. **Modeling** (`src/main/python/taf/modeling/`) — Browser, RESTClient, CLIRunner, Page Objects
3. **Foundation** (`src/main/python/taf/foundation/`) — ServiceLocator, Configuration (YAML), Utils
4. **Plugins** (`src/main/python/taf/foundation/plugins/`) — Concrete implementations discovered at runtime via ServiceLocator

Plugin interfaces in `taf/foundation/api/plugins/`:

| Interface | Implementation | Status |
|-----------|----------------|--------|
| `WebPlugin` | `SeleniumPlugin` (Selenium 4, headless) | Implemented |
| `RESTPlugin` | `RequestsPlugin` | Implemented |
| `CLIPlugin` | `ParamikoPlugin` | Implemented |
| `MobilePlugin` | `AppiumPlugin` | Implemented |
| `WebPlugin` | `PlaywrightPlugin` | Planned (T.1.3) |
| `RESTPlugin` | `HttpxPlugin` (async) | Planned (T.1.3) |
| `WSPlugin` | `WebSocketPlugin` | Planned (T.1.3) |
| `LLMPlugin` | `LLMJudgePlugin` | Planned (T.1.3) |

## Build & Test

```bash
# Lint
flake8 src/main/python/ src/test/python/ --max-line-length=120

# Type check
mypy src/main/python/taf/ --ignore-missing-imports

# Framework unit tests (42 tests, all pass)
PYTHONPATH=src/main/python pytest src/test/python/ut/ -v
```

## Conventions

- **Files/dirs**: lowercase-with-hyphens for directories, lowercase_with_underscores for Python modules.
- **Plugins**: One plugin class per file. File named `<name>plugin.py` (e.g., `playwrightplugin.py`).
- **Plugin interfaces**: Abstract base in `taf/foundation/api/plugins/`. Concrete in `taf/foundation/plugins/<type>/<name>/`.
- **Modeling**: High-level wrappers in `taf/modeling/<type>/`. Must use ServiceLocator to resolve plugins, never import concrete plugins directly.
- **Config**: YAML files in `taf/foundation/conf/` (framework). Environment variables override YAML values (`TAF_PLUGIN_<NAME>_<KEY>`).
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
2. Create concrete implementation in `taf/foundation/plugins/<type>/<name>/`
3. Register in `taf/foundation/conf/config.yml`
4. Add modeling wrapper in `taf/modeling/<type>/` if needed
5. Write unit test in `src/test/python/ut/`

## Pitfalls

- **Never import concrete plugins in test code** — always go through ServiceLocator or modeling layer. Direct imports break plugin swappability.
- **ServiceLocator is a singleton** — plugin resolution happens once per type. Configuration must be set before first access.
- **config.yml `location` is relative** — plugin paths are relative to `taf/foundation/conf/`. Use `../plugins/...` pattern.
- **Selenium 4 API** — use `find_elements(By.ID, value)` not deprecated `find_elements_by_id()`. Use `Service` and `Options`, not `executable_path` or `desired_capabilities`.
- **BDD tests use behave, not pytest-bdd** — existing examples in `src/test/python/bpt/bdd/` use behave with Gherkin.
