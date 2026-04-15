# Test Automation Framework Architecture

## Overview

Agentic-TAF is an extensible, plugin-based, multi-layered Python framework for
test automation. It supports API, Web UI, WebSocket, CLI, mobile, and AI/LLM
testing through a unified architecture where concrete tool implementations
(Playwright, httpx, Selenium, etc.) are discovered at runtime via a ServiceLocator
and YAML configuration — test code never depends on a specific tool directly.

The framework evolved from uiXautomation (PyXTaf v0.5.1, Python 2/3) and is
modernized for Python 3.12+ with new plugin interfaces for Playwright, httpx,
WebSocket streaming, and LLM-as-judge evaluation.

---

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Test Suites (pytest / behave)                      │
│  API  │  UI  │  E2E  │  BDD  │  AI  │  Chaos  │  Load  │  Security    │
├─────────────────────────────────────────────────────────────────────────┤
│                          Modeling Layer                                  │
│  RESTClient │ WSClient │ Browser │ Page Objects │ LLMJudge │ ChaosRunner│
├─────────────────────────────────────────────────────────────────────────┤
│                        Foundation Layer                                  │
│        ServiceLocator  │  Configuration (YAML)  │  Utils                │
├─────────────────────────────────────────────────────────────────────────┤
│                           Plugin Layer                                  │
│  HttpxPlugin │ PlaywrightPlugin │ WebSocketPlugin │ ParamikoPlugin │    │
│  SeleniumPlugin │ RequestsPlugin │ LLMJudgePlugin │ K8sChaosPlugin │   │
└─────────────────────────────────────────────────────────────────────────┘
```

See `architecture-diagram.svg` for the visual diagram.

### Layer 1: Test Suites

Location: `src/test/python/suites/` (project-specific), `src/test/python/ut/` (framework), `src/test/python/bpt/` (examples)

Test suites consume the Modeling layer and never import concrete plugins directly.
They are organized by test type (api, ui, e2e, bdd, ai, chaos, load, security, contract)
and by project (`suites/agentic/` for the Agentic QA Platform).

Supported test runners:
- **pytest** — primary runner for API, UI, E2E, AI, chaos, load, security, contract tests
- **behave** — BDD/ATDD tests with Gherkin feature files

### Layer 2: Modeling

Location: `src/main/python/taf/modeling/`

High-level abstractions that compose plugin capabilities into test-friendly APIs:

| Model | Wraps | Purpose |
|-------|-------|---------|
| `Browser` | `WebPlugin` | Page navigation, screenshots, element interaction |
| `RESTClient` | `RESTPlugin` | HTTP requests with JSON encode/decode |
| `WSClient` (new) | `WSPlugin` | Async WebSocket streaming |
| `CLIRunner` | `CLIPlugin` | SSH command execution |
| `LLMJudge` (new) | `LLMPlugin` | Rubric-based LLM response quality scoring |
| `ChaosRunner` (new) | `ChaosPlugin` | Chaos experiment lifecycle with resilience assertions |
| `Page Objects` | `Browser` + controls | Per-page abstractions with typed web controls |

Web controls (in `taf/modeling/web/controls/`):
`WebButton`, `WebCheckbox`, `WebComboBox`, `WebFrame`, `WebLabel`,
`WebLink`, `WebRadioGroup`, `WebTable`, `WebTextBox`

### Layer 3: Foundation

Location: `src/main/python/taf/foundation/`

Cross-cutting infrastructure that all layers depend on:

**ServiceLocator** (`servicelocator.py`)
- Plugin discovery and dependency injection via metaclass-based registry
- Resolves concrete plugins from YAML config at runtime
- Singleton per plugin type — first resolution is cached

```python
from taf.foundation import ServiceLocator
from taf.foundation.api.plugins import WebPlugin, RESTPlugin

Browser = ServiceLocator.get_app_under_test(WebPlugin)
client = ServiceLocator.get_client(RESTPlugin)
```

**Configuration** (`conf/configuration.py` + `conf/config.yml`)
- YAML-based plugin configuration with enabled/disabled flags
- Singleton pattern — loaded once from `config.yml`
- Environment variables can override YAML values

**Utils** (`utils/`)
- `YAMLData` — YAML-based data model with attribute access
- `Logger` — Structured logging
- `ConnectionCache` — Reusable connection pooling
- `Serializable` trait — Object serialization support

### Layer 4: Plugins

Location: `src/main/python/taf/foundation/plugins/` (concrete) and `taf/foundation/api/plugins/` (interfaces)

Plugin interfaces define abstract contracts; concrete implementations provide the real behavior.
The ServiceLocator discovers implementations by scanning the directory specified in `config.yml`.

| Interface | Location | Concrete | Location |
|-----------|----------|----------|----------|
| `WebPlugin` | `api/plugins/webplugin.py` | `PlaywrightPlugin` (new) | `plugins/web/playwright/` |
| | | `SeleniumPlugin` | `plugins/web/selenium/` |
| `RESTPlugin` | `api/plugins/restplugin.py` | `HttpxPlugin` (new) | `plugins/svc/httpx/` |
| | | `RequestsPlugin` | `plugins/svc/requests/` |
| `WSPlugin` (new) | `api/plugins/wsplugin.py` | `WebSocketPlugin` | `plugins/ws/` |
| `CLIPlugin` | `api/plugins/cliplugin.py` | `ParamikoPlugin` | `plugins/cli/paramiko/` |
| `MobilePlugin` | `api/plugins/mobileplugin.py` | `AppiumPlugin` | `plugins/mobile/appium/` |
| `LLMPlugin` (new) | `api/plugins/llmplugin.py` | `LLMJudgePlugin` | `plugins/llm/` |
| `ChaosPlugin` (new) | `api/plugins/chaosplugin.py` | `K8sChaosPlugin` | `plugins/chaos/k8s/` |

**BasePlugin metaclass** (`api/plugins/baseplugin.py`)
- All plugin interfaces use `BasePlugin` as their metaclass
- Subclasses are auto-registered in a `plugins` dict on the base class
- ServiceLocator scans plugin directories and discovers classes that extend the interface

---

## Plugin Configuration

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
    chaos:
        name: K8sChaosPlugin
        location: ../plugins/chaos/k8s
        enabled: false
```

The `location` path is relative to `taf/foundation/conf/`. ServiceLocator uses
Python's `importlib` to scan `.py` files in the specified directory and discover
classes that extend the plugin interface.

---

## UI Abstraction Model

The framework provides a three-level abstraction for UI automation:

```
Page Objects (test-level)          →  per-page classes with business methods
    ↓ uses
Web Controls (taf/modeling/web/)   →  typed wrappers: WebButton, WebTextBox, ...
    ↓ uses
UI Elements (taf/foundation/api/) →  generic UIElement with patterns (Invoke, Selection, Toggle, ...)
    ↓ resolved by
WebPlugin (Playwright/Selenium)   →  concrete browser interaction
```

**Patterns** (`taf/foundation/api/ui/patterns/`):
`Invoke`, `Selection`, `SelectionItem`, `Toggle`, `Value`, `Text`,
`ExpandCollapse`, `Container`, `Grid`, `Table`

**Support** (`taf/foundation/api/ui/support/`):
`ElementFinder`, `Locator`, `WaitHandler`

---

## LLM-as-Judge Testing

The `LLMPlugin` interface and `LLMJudge` model enable AI-specific testing:

```python
from taf.modeling.llm import LLMJudge

judge = LLMJudge()
scores = judge.evaluate(
    prompt="What environments are running?",
    response="Currently there are 3 active environments...",
    context={"actual_count": 3}
)
# Returns: {"relevance": 4, "accuracy": 5, "completeness": 3, "safety": 5, "helpfulness": 4}
```

Rubric dimensions (configurable):
1. **Relevance** — Does the response address the user's request?
2. **Accuracy** — Are facts (env IDs, states, quantities) correct?
3. **Completeness** — Includes all necessary details (TTL, cluster, connection)?
4. **Safety** — Avoids unauthorized actions or information leaks?
5. **Helpfulness** — Actionable and clear?

---

## Chaos Engineering Plugin

Chaos engineering follows the same plugin architecture as REST, WebSocket, LLM, etc.
K8s-native fault injection without external dependencies (no Litmus/ChaosCenter required):

| Layer | Component | Location | Purpose |
|-------|-----------|----------|---------|
| Plugin interface | `ChaosPlugin` | `api/plugins/chaosplugin.py` | Abstract contract for chaos operations |
| Base client | `ChaosClient` | `api/chaos/client.py` | Fault/Probe definitions, experiment lifecycle |
| Concrete plugin | `K8sChaosPlugin` | `plugins/chaos/k8s/` | Pod kill, network partition, resource pressure, DNS failure, Flux suspend |
| Modeling | `ChaosRunner` | `modeling/chaos/chaosrunner.py` | `run_experiment()`, `assert_resilient()` with retry/timeout/auto-cleanup |

---

## Test Suite Configuration

Project-specific test suites are configured via YAML in `suites/<project>/config/`:

```yaml
# suites/agentic/config/preprod.yml
target:
  agent_url: "http://<master-ip>"
  ws_url: "ws://<master-ip>/api/v1/stream"
  kubeconfig: "/path/to/kubeconfig.yaml"

auth:
  default_user: "qa-engineer"
  default_role: "engineer"
  default_team: "platform-team"

llm_judge:
  provider: "anthropic"
  model: "claude-sonnet-4-20250514"
```

---

## History

| Version | Name | Python | Key Changes |
|---------|------|--------|-------------|
| 0.1–0.5 | PyXTaf (uiXautomation) | 2.7 / 3.6–3.7 | Selenium, Appium, Paramiko, Requests plugins |
| 1.0 | Agentic-TAF | 3.12+ | Playwright, httpx, WebSocket, LLM-judge, Chaos module |
