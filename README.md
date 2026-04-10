# Agentic-TAF

Agentic Test Automation Framework — an extensible, plugin-based, multi-layered framework for test automation across API, Web UI, WebSocket, CLI, and AI/LLM validation.

Evolved from [PyXTaf](https://pypi.org/project/PyXTaf/) (uiXautomation), modernized for Python 3.12+ with Playwright, httpx, and LLM-as-judge capabilities.

## Architecture

### Multi-Layer Architecture (v1.0)

![Agentic-TAF Architecture](architecture-diagram.svg "Agentic-TAF Multi-Layer Architecture")

<details>
<summary>Original PyXTaf architecture (v0.x)</summary>

![PyXTaf Diagram](diagram.png?raw=true "PyXTaf Architecture Diagram (original)")
</details>

### Layer Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Test Suites (pytest / behave)                   │
│  API  │  UI  │  E2E  │  BDD  │  AI  │  Chaos  │  Load  │  Security    │
├─────────────────────────────────────────────────────────────────────────┤
│                          Modeling Layer                                  │
│  RESTClient  │  WSClient  │  Browser  │  Page Objects  │  LLMJudge     │
├─────────────────────────────────────────────────────────────────────────┤
│                           Plugin Layer                                  │
│  HttpxPlugin │ PlaywrightPlugin │ WebSocketPlugin │ ParamikoPlugin │    │
│  SeleniumPlugin │ RequestsPlugin │ LLMJudgePlugin │ AppiumPlugin   │    │
├─────────────────────────────────────────────────────────────────────────┤
│                        Foundation Layer                                  │
│  ServiceLocator  │  Configuration (YAML)  │  Utils  │  Chaos Module    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Plugin Architecture

The framework uses a **ServiceLocator** pattern with pluggable backends. Each plugin type defines an interface; concrete implementations are discovered at runtime via YAML configuration.

| Plugin Interface | Concrete Implementations | Purpose |
|------------------|--------------------------|---------|
| `WebPlugin` | `PlaywrightPlugin` (new), `SeleniumPlugin` (existing) | Browser automation |
| `RESTPlugin` | `HttpxPlugin` (new, async), `RequestsPlugin` (existing) | REST API testing |
| `WSPlugin` (new) | `WebSocketPlugin` | WebSocket streaming |
| `CLIPlugin` | `ParamikoPlugin` (existing) | SSH / CLI access |
| `MobilePlugin` | `AppiumPlugin` (existing) | Mobile automation |
| `LLMPlugin` (new) | `LLMJudgePlugin` | LLM response quality evaluation |

### Layer Descriptions

**Foundation** (`taf/foundation/`)
- `ServiceLocator` — Plugin discovery and dependency injection via metaclass-based registry
- `Configuration` — YAML-based config with environment variable overrides
- `BasePlugin` — Metaclass that auto-registers plugin implementations
- `Utils` — Logger, YAML data model, connection cache, serialization traits

**Modeling** (`taf/modeling/`)
- High-level abstractions that compose plugin capabilities into test-friendly APIs
- `Browser` — Page navigation, screenshot, element interaction (wraps WebPlugin)
- `RESTClient` — HTTP client with JSON encode/decode (wraps RESTPlugin)
- `WSClient` (new) — Async WebSocket streaming client (wraps WSPlugin)
- `CLIRunner` — SSH command execution (wraps CLIPlugin)
- `LLMJudge` (new) — Rubric-based LLM response scoring (wraps LLMPlugin)

**Chaos** (`taf/chaos/`) (new)
- K8s-native fault injection (pod kill, network partition, resource pressure)
- Resilience probes (HTTP health, K8s resource, Prometheus query)
- Experiment orchestrator for structured chaos testing

**Test Suites** (`src/test/python/suites/`)
- Project-specific test suites that exercise target systems as black-box consumers
- Framework unit tests in `src/test/python/ut/`
- BDD/ATDD examples in `src/test/python/bpt/`

## Project Structure

```
agentic-taf/
├── src/
│   ├── main/python/taf/                    # Framework core
│   │   ├── foundation/
│   │   │   ├── api/
│   │   │   │   ├── plugins/                # Plugin interfaces
│   │   │   │   │   ├── baseplugin.py       # Metaclass plugin registry
│   │   │   │   │   ├── webplugin.py        # Browser automation interface
│   │   │   │   │   ├── restplugin.py       # REST API interface
│   │   │   │   │   ├── cliplugin.py        # SSH/CLI interface
│   │   │   │   │   ├── mobileplugin.py     # Mobile interface
│   │   │   │   │   ├── wsplugin.py         # WebSocket interface (new)
│   │   │   │   │   └── llmplugin.py        # LLM-as-judge interface (new)
│   │   │   │   ├── ui/                     # UI element abstractions
│   │   │   │   │   ├── controls/           # Button, Checkbox, Edit, etc.
│   │   │   │   │   ├── patterns/           # Invoke, Selection, Toggle, etc.
│   │   │   │   │   └── support/            # Locator, ElementFinder, WaitHandler
│   │   │   │   ├── svc/REST/               # REST client base class
│   │   │   │   └── cli/                    # CLI client base class
│   │   │   ├── plugins/                    # Concrete implementations
│   │   │   │   ├── web/playwright/         # Playwright plugin (new)
│   │   │   │   ├── web/selenium/           # Selenium plugin (existing)
│   │   │   │   ├── svc/httpx/              # httpx async plugin (new)
│   │   │   │   ├── svc/requests/           # requests plugin (existing)
│   │   │   │   ├── ws/                     # WebSocket plugin (new)
│   │   │   │   ├── cli/paramiko/           # Paramiko SSH plugin (existing)
│   │   │   │   ├── mobile/appium/          # Appium plugin (existing)
│   │   │   │   └── llm/                    # LLM judge plugin (new)
│   │   │   ├── conf/                       # YAML config + loader
│   │   │   ├── servicelocator.py           # Plugin DI container
│   │   │   └── utils/                      # Logger, YAMLData, traits
│   │   ├── modeling/                       # High-level test models
│   │   │   ├── web/                        # Browser + typed web controls
│   │   │   ├── svc/                        # RESTClient
│   │   │   ├── cli/                        # CLIRunner
│   │   │   ├── ws/                         # WSClient (new)
│   │   │   └── llm/                        # LLMJudge (new)
│   │   └── chaos/                          # K8s chaos module (new)
│   │
│   └── test/python/
│       ├── ut/                             # Framework unit tests
│       ├── bpt/                            # BDD/ATDD examples
│       └── suites/                         # Project-specific test suites
│           └── agentic/                    # Agentic QA Platform tests
│               ├── api/                    # REST + WebSocket API tests
│               ├── ui/                     # Playwright UI tests + page objects
│               ├── e2e/                    # End-to-end provisioning flows
│               ├── bdd/                    # Gherkin + behave scenarios
│               ├── ai/                     # LLM-as-judge, tool selection, injection
│               ├── chaos/                  # Platform chaos experiments
│               ├── load/                   # Performance / throughput tests
│               ├── security/              # RBAC, auth, secret tests
│               ├── contract/              # OpenAPI schema validation
│               └── config/                # preprod.yml, dev.yml, ci.yml
│
├── pyproject.toml                          # Build config (replaces setup.py + PyBuilder)
├── conftest.py                             # Global pytest configuration
├── Dockerfile                              # Test runner container
├── docker-compose.yml                      # Local dev services
└── README.md
```

## Installation

```bash
# From source (development)
pip install -e ".[dev]"

# Run framework unit tests
pytest src/test/python/ut/ -v

# Run agentic platform test suites
pytest src/test/python/suites/agentic/ -v --config=preprod
```

## Plugin Configuration

Plugins are configured via YAML and discovered by the ServiceLocator at runtime:

```yaml
# taf/foundation/conf/config.yml
plugins:
    web:
        name: PlaywrightPlugin
        location: ../plugins/web/playwright
        enabled: true
    rest:
        name: HttpxPlugin
        location: ../plugins/svc/httpx
        enabled: true
    websocket:
        name: WebSocketPlugin
        location: ../plugins/ws
        enabled: true
    cli:
        name: ParamikoPlugin
        location: ../plugins/cli/paramiko
        enabled: true
    llm:
        name: LLMJudgePlugin
        location: ../plugins/llm
        enabled: true
    mobile:
        name: AppiumPlugin
        location: ../plugins/mobile/appium
        enabled: false
```

## Key Concepts

### ServiceLocator

```python
from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import WebPlugin, RESTPlugin

# Get browser (resolves PlaywrightPlugin or SeleniumPlugin based on config)
Browser = ServiceLocator.get_app_under_test(WebPlugin)

# Get REST client (resolves HttpxPlugin or RequestsPlugin based on config)
client = ServiceLocator.get_client(RESTPlugin)
```

### Page Object Model

```python
from taf.modeling.web import Browser
from taf.modeling.web.controls import WebButton, WebTextBox

class LoginPage:
    def __init__(self, browser: Browser):
        self.username = WebTextBox(locator="[data-testid='username']")
        self.password = WebTextBox(locator="[data-testid='password']")
        self.submit = WebButton(locator="[data-testid='login-btn']")

    def login(self, user: str, password: str):
        self.username.set_text(user)
        self.password.set_text(password)
        self.submit.click()
```

### LLM-as-Judge

```python
from taf.modeling.llm import LLMJudge

judge = LLMJudge()
scores = judge.evaluate(
    prompt="What environments are running?",
    response="Currently there are 3 active environments...",
    context={"actual_count": 3}
)
assert scores["accuracy"] >= 4  # 1-5 scale
```

## History

This project was originally created as **uiXautomation** (PyXTaf) — a Python 2/3 compatible
test automation framework with Selenium, Appium, Paramiko, and Requests plugins. It has been
renamed to **Agentic-TAF** and modernized for Python 3.12+ with new plugin interfaces for
Playwright, httpx, WebSocket, and LLM-as-judge testing.

## License

[GNU Lesser General Public License v3.0 (LGPL-3.0)](LICENSE)
