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

1. **Test Suites** (`src/test/python/suites/`) — pytest/behave tests: API, UI, E2E, BDD, AI, Chaos, Load, Security
2. **Modeling** (`src/main/python/taf/modeling/`) — High-level abstractions: Browser, RESTClient, WSClient, CLIRunner, LLMJudge, Page Objects
3. **Foundation** (`src/main/python/taf/foundation/`) — ServiceLocator, Configuration (YAML), Utils, Chaos Module
4. **Plugins** (`src/main/python/taf/foundation/plugins/`) — Concrete implementations discovered at runtime via ServiceLocator

Plugin interfaces in `taf/foundation/api/plugins/`:

| Interface | Implementations | Purpose |
|-----------|----------------|---------|
| `WebPlugin` | PlaywrightPlugin, SeleniumPlugin | Browser automation |
| `RESTPlugin` | HttpxPlugin, RequestsPlugin | REST API testing |
| `WSPlugin` | WebSocketPlugin | WebSocket streaming |
| `CLIPlugin` | ParamikoPlugin | SSH/CLI access |
| `MobilePlugin` | AppiumPlugin | Mobile automation |
| `LLMPlugin` | LLMJudgePlugin | LLM response quality scoring |

## Build & Test

```bash
# Lint
flake8 src/main/python/ src/test/python/ --max-line-length=120

# Type check
mypy src/main/python/taf/ --ignore-missing-imports

# Framework unit tests
pytest src/test/python/ut/ -v

# Agentic platform test suites (requires preprod cluster access)
pytest src/test/python/suites/agentic/api/ -v
pytest src/test/python/suites/agentic/ui/ -v --headless
pytest src/test/python/suites/agentic/ai/ -v

# BDD scenarios
behave src/test/python/suites/agentic/bdd/features/

# All tests
pytest src/test/python/ -v --ignore=src/test/python/suites/agentic/chaos/ --ignore=src/test/python/suites/agentic/load/
```

## Conventions

- **Files/dirs**: lowercase-with-hyphens for directories, lowercase_with_underscores for Python modules.
- **Plugins**: One plugin class per file. File named `<name>plugin.py` (e.g., `playwrightplugin.py`).
- **Plugin interfaces**: Abstract base in `taf/foundation/api/plugins/`. Concrete in `taf/foundation/plugins/<type>/<name>/`.
- **Modeling**: High-level wrappers in `taf/modeling/<type>/`. Must use ServiceLocator to resolve plugins, never import concrete plugins directly.
- **Test suites**: Under `src/test/python/suites/<project>/`. Each suite type in its own subdirectory (api/, ui/, ai/, etc.).
- **Page Objects**: Under `suites/<project>/ui/pages/`. One class per page. Use modeling layer controls, not raw Playwright/Selenium.
- **Config**: YAML files in `taf/foundation/conf/` (framework) and `suites/<project>/config/` (project-specific). Environment variables override YAML values.
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

### Adding a test suite

1. Create directory under `src/test/python/suites/<project>/<type>/`
2. Add `conftest.py` with fixtures using the modeling layer
3. Write tests using pytest conventions
4. Add config in `suites/<project>/config/<env>.yml`

## Pitfalls

- **Never import concrete plugins in test code** — always go through ServiceLocator or modeling layer. Direct imports break plugin swappability.
- **Python 2 code still exists** — the framework was originally Py2/3 compatible. Modernization will remove Py2 patterns. Until then, some files use `super(ClassName, self).__init__()` and `__metaclass__`.
- **ServiceLocator is a singleton** — plugin resolution happens once per type. Configuration must be set before first access.
- **config.yml `location` is relative** — plugin paths are relative to `taf/foundation/conf/`. Use `../plugins/...` pattern.
- **Existing Selenium plugin has a bundled ChromeDriver binary** — do not commit browser binaries. Playwright manages its own browsers.
- **BDD tests use behave, not pytest-bdd** — existing examples in `src/test/python/bpt/bdd/` use behave with Gherkin.
