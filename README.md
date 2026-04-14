# Agentic-TAF

Agentic Test Automation Framework — an extensible, plugin-based, multi-layered framework for test automation across API, Web UI, WebSocket, CLI, and AI/LLM validation.

Evolved from [PyXTaf](https://pypi.org/project/PyXTaf/) (uiXautomation), modernized for Python 3.12+.

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
│  Unit tests (ut/)  │  BDD/ATDD examples (bpt/)  │  Platform (planned)  │
├─────────────────────────────────────────────────────────────────────────┤
│                          Modeling Layer                                  │
│  RESTClient │ Browser │ CLIRunner │ WSClient │ LLMJudge │ ChaosRunner  │
├─────────────────────────────────────────────────────────────────────────┤
│                           Plugin Layer                                  │
│  Selenium │ Playwright │ Requests │ httpx │ WS │ Paramiko │ LLM │ K8s │
├─────────────────────────────────────────────────────────────────────────┤
│                        Foundation Layer                                  │
│        ServiceLocator  │  Configuration (YAML)  │  Utils               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Plugin Architecture

The framework uses a **ServiceLocator** pattern with pluggable backends. Each plugin type defines an interface; concrete implementations are discovered at runtime via YAML configuration.

**Implemented:**

| Plugin Interface | Implementation | Purpose |
|------------------|----------------|---------|
| `WebPlugin` | `SeleniumPlugin` (default) | Browser automation (Selenium 4, headless) |
| `WebPlugin` | `PlaywrightPlugin` (optional) | Browser automation (Playwright, headless) |
| `RESTPlugin` | `RequestsPlugin` (default) | REST API testing (requests) |
| `RESTPlugin` | `HttpxRESTPlugin` (optional) | REST API testing (httpx) |
| `WSPlugin` | `WebSocketPlugin` (optional) | WebSocket streaming (websockets) |
| `CLIPlugin` | `ParamikoPlugin` | SSH / CLI access |
| `MobilePlugin` | `AppiumPlugin` | Mobile automation |
| `LLMPlugin` | `LLMJudgePlugin` (optional) | LLM response quality evaluation (OpenAI/Anthropic) |
| `ChaosPlugin` | `K8sChaosPlugin` (optional) | K8s chaos engineering (pod kill, network partition, Flux suspend) |

> **Optional plugins** require their dependency installed (`pip install agentic-taf[chaos]`, etc.)
> and a config.yml change to enable. Defaults remain Selenium + Requests.

### Layer Descriptions

**Foundation** (`taf/foundation/`)
- `ServiceLocator` — Plugin discovery and dependency injection via metaclass-based registry
- `Configuration` — YAML-based config with environment variable overrides (`TAF_PLUGIN_<NAME>_<KEY>`)
- `BasePlugin` — Metaclass that auto-registers plugin implementations
- `Utils` — Logger, YAML data model, connection cache, serialization traits

**Modeling** (`taf/modeling/`)
- High-level abstractions that compose plugin capabilities into test-friendly APIs
- `Browser` — Page navigation, screenshot, element interaction (wraps WebPlugin)
- `RESTClient` — HTTP client with JSON encode/decode (wraps RESTPlugin)
- `CLIRunner` — SSH command execution (wraps CLIPlugin)
- `WSClient` — WebSocket streaming with `collect()`, `collect_text()`, `send_and_receive()`
- `LLMJudge` — LLM-as-judge with `assert_quality()` threshold assertions (OpenAI/Anthropic)
- `ChaosRunner` — Chaos experiment lifecycle with `assert_resilient()` retry/timeout

**Test Suites** (`src/test/python/`)
- `ut/` — 142 framework unit tests (all pass)
- `suites/agentic/api/` — 21 E2E API tests (contract, functional, state machine)
- `suites/agentic/security/` — 8 E2E security tests (RBAC, secret exposure, injection)
- `suites/agentic/ui/` — 10 E2E UI tests (Playwright, engine-agnostic Page Objects)
- `suites/agentic/ai/` — 11 E2E AI tests (LLM-as-judge evaluation, adversarial, fallback; skip if LLM down)
- `bpt/` — BDD/ATDD examples (Bing search, httpbin API)

## Project Structure

```
agentic-taf/
├── src/
│   ├── main/python/taf/                    # Framework core
│   │   ├── foundation/
│   │   │   ├── api/
│   │   │   │   ├── plugins/                # Plugin interfaces (7 types)
│   │   │   │   ├── ui/                     # UI element abstractions
│   │   │   │   ├── svc/REST/               # REST client base class
│   │   │   │   ├── cli/                    # CLI client base class
│   │   │   │   ├── ws/                     # WebSocket client base class
│   │   │   │   ├── llm/                    # LLM client base class
│   │   │   │   └── chaos/                  # Chaos client base class
│   │   │   ├── plugins/                    # Concrete implementations (9 plugins)
│   │   │   │   ├── web/selenium/           # SeleniumPlugin (default)
│   │   │   │   ├── web/playwright/         # PlaywrightPlugin (optional)
│   │   │   │   ├── svc/requests/           # RequestsPlugin (default)
│   │   │   │   ├── svc/httpx/              # HttpxRESTPlugin (optional)
│   │   │   │   ├── ws/websocket/           # WebSocketPlugin (optional)
│   │   │   │   ├── cli/paramiko/           # ParamikoPlugin
│   │   │   │   ├── mobile/appium/          # AppiumPlugin
│   │   │   │   ├── llm/judge/              # LLMJudgePlugin (optional)
│   │   │   │   └── chaos/k8s/              # K8sChaosPlugin (optional)
│   │   │   ├── conf/                       # YAML config + loader
│   │   │   ├── servicelocator.py           # Plugin DI container
│   │   │   └── utils/                      # Logger, YAMLData, traits
│   │   └── modeling/                       # High-level test models (6 types)
│   │       ├── web/                        # Browser + typed web controls
│   │       ├── svc/                        # RESTClient
│   │       ├── cli/                        # CLIRunner
│   │       ├── ws/                         # WSClient
│   │       ├── llm/                        # LLMJudge
│   │       └── chaos/                      # ChaosRunner
│   │
│   └── test/python/
│       ├── ut/                             # Framework unit tests (142 tests)
│       ├── suites/agentic/                 # Platform E2E test suites
│       │   ├── api/                        # API tests (21 tests)
│       │   ├── security/                   # Security tests (8 tests)
│       │   ├── ui/                         # UI tests (10 tests, Playwright)
│       │   │   └── pages/                  # Page Objects (engine-agnostic)
│       │   ├── ai/                         # AI tests (11 tests, LLMJudge)
│       │   ├── config/                     # Environment configs
│       │   └── contract/schemas/           # OpenAPI schema
│       └── bpt/                            # BDD/ATDD examples
│
├── Jenkinsfile                             # Jenkins CI pipeline
├── pyproject.toml                          # Build config + dependencies
├── .github/workflows/ci.yml               # CI: lint → test (JUnit + coverage) → build
└── README.md
```

## Installation

```bash
# From source (development)
pip install -r src/main/python/requirements-dev.txt

# Or via pyproject.toml extras
pip install -e ".[dev]"

# Run framework unit tests
PYTHONPATH=src/main/python pytest src/test/python/ut/ -v
```

## Plugin Configuration

Plugins are configured via YAML and discovered by the ServiceLocator at runtime:

```yaml
# taf/foundation/conf/config.yml
plugins:
    web:
        name: SeleniumPlugin
        location: ../plugins/web/selenium
        enabled: true
    cli:
        name: ParamikoPlugin
        location: ../plugins/cli/paramiko
        enabled: true
    REST:
        name: RequestsPlugin
        location: ../plugins/svc/requests
        enabled: true
    mobile:
        name: AppiumPlugin
        location: ../plugins/mobile/appium
        enabled: false
```

Override via environment variables: `TAF_PLUGIN_WEB_ENABLED=false`

## Key Concepts

### ServiceLocator

```python
from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import WebPlugin, RESTPlugin

# Get browser (resolves SeleniumPlugin based on config)
Browser = ServiceLocator.get_app_under_test(WebPlugin)

# Get REST client (resolves RequestsPlugin based on config)
client = ServiceLocator.get_client(RESTPlugin)
```

### Page Object Model

```python
from taf.modeling.web import Browser
from taf.modeling.web import WebButton, WebTextBox

browser = Browser(name='chrome', headless=True)
browser.launch('http://example.com')

txt_search = WebTextBox(id='search_box')
btn_go = WebButton(id='submit_btn')
txt_search.set('test query')
btn_go.click()
```

## History

This project was originally created as **uiXautomation** (PyXTaf) — a Python 2/3 compatible
test automation framework with Selenium, Appium, Paramiko, and Requests plugins. It has been
renamed to **Agentic-TAF** and modernized for Python 3.12+ with Selenium 4 support.

New plugin interfaces (Playwright, httpx, WebSocket, LLM-as-judge) and platform test suites
are planned — see [docs/implementation-plan.md](docs/implementation-plan.md) for the roadmap.

## License

[GNU Lesser General Public License v3.0 (LGPL-3.0)](LICENSE)
