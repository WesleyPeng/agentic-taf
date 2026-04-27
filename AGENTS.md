# Agentic-TAF

See `CLAUDE.md` for conventions, build commands, and pitfalls.
This file contains reference tables and implementation rules.

## Repository Structure

```
agentic-taf/
├── src/main/python/taf/              # Framework core (package: taf)
│   ├── foundation/
│   │   ├── api/plugins/              # Plugin INTERFACES (abstract)
│   │   │   ├── baseplugin.py         # BasePlugin metaclass
│   │   │   ├── webplugin.py          # WebPlugin — browser automation
│   │   │   ├── restplugin.py         # RESTPlugin — REST API
│   │   │   ├── cliplugin.py          # CLIPlugin — SSH/CLI
│   │   │   ├── mobileplugin.py       # MobilePlugin — mobile
│   │   │   ├── wsplugin.py           # WSPlugin — WebSocket
│   │   │   ├── llmplugin.py          # LLMPlugin — LLM judge
│   │   │   └── chaosplugin.py        # ChaosPlugin — chaos engineering
│   │   ├── api/ui/                   # UI element abstractions (controls, patterns, support)
│   │   ├── api/svc/REST/             # REST client base class
│   │   ├── api/cli/                  # CLI client base class
│   │   ├── api/ws/                   # WebSocket client base class
│   │   ├── api/llm/                  # LLM client base class (provider-agnostic)
│   │   ├── api/chaos/                # Chaos client base class (Fault, Probe, experiment)
│   │   ├── plugins/                  # CONCRETE implementations
│   │   │   ├── web/selenium/         # SeleniumPlugin (Selenium 4, headless)
│   │   │   ├── web/playwright/       # PlaywrightPlugin (optional)
│   │   │   ├── svc/requests/         # RequestsPlugin
│   │   │   ├── svc/httpx/            # HttpxRESTPlugin (optional)
│   │   │   ├── ws/websocket/         # WebSocketPlugin (optional)
│   │   │   ├── cli/paramiko/         # ParamikoPlugin
│   │   │   ├── mobile/appium/        # AppiumPlugin (stub / planned)
│   │   │   ├── llm/judge/            # LLMJudgePlugin (optional, OpenAI/Anthropic)
│   │   │   └── chaos/k8s/            # K8sChaosPlugin (optional, faults + probes)
│   │   ├── conf/                     # config.yml + Configuration loader
│   │   ├── servicelocator.py         # Plugin DI container
│   │   └── utils/                    # Logger, YAMLData, ConnectionCache, traits
│   └── modeling/                     # High-level test models
│       ├── web/                      # Browser + typed web controls
│       ├── svc/                      # RESTClient
│       ├── cli/                      # CLIRunner
│       ├── ws/                       # WSClient (streaming, collect, send_and_receive)
│       ├── llm/                      # LLMJudge (threshold assertions, provider-agnostic)
│       └── chaos/                    # ChaosRunner (experiment lifecycle, assert_resilient)
│
├── src/test/python/
│   ├── ut/                           # Framework unit tests (274 tests)
│   ├── bpt/                          # BDD/ATDD examples (Bing, httpbin)
│   └── suites/agentic/              # Platform E2E test suites
│       ├── api/                      # T.2: API tests (21 tests)
│       ├── security/                 # T.8: Security tests (8 tests)
│       ├── ui/                       # T.3: UI tests (10 tests, Playwright)
│       │   └── pages/                # Page Objects (engine-agnostic)
│       ├── ai/                       # T.4: 11 baseline AI tests + T.10: 5 ground-truth/multi-turn = 16 tests
│       │   ├── test_ai.py            # T.4 (11 tests, graceful skip)
│       │   └── test_e2e_quality.py   # T.10 (5 tests, ground-truth + multi-turn)
│       ├── bdd/features/             # T.5: BDD scenarios (10 scenarios across 4 feature files, behave)
│       │   └── steps/                # Step definitions
│       ├── chaos/                    # T.6: Chaos experiments (4 tests, K8sChaosPlugin)
│       ├── load/                     # T.7: Load & performance tests (4 tests)
│       ├── reporting/                # T.9: CI utility (JUnit to OpenSearch push, not a test suite)
│       ├── config/preprod.yml        # Environment config
│       ├── conftest.py               # Shared fixtures (ServiceLocator → HttpClient)
│       └── contract/schemas/         # OpenAPI schema
│
├── docs/
│   ├── architecture.md               # Architecture deep-dive
│   └── implementation-plan.md        # Task tracker (T.1–T.9)
│
├── CLAUDE.md                         # AI agent conventions (this project)
├── AGENTS.md                         # Reference tables (this file)
├── README.md                         # Project overview
├── Jenkinsfile                       # Jenkins CI pipeline (E2E stages gated by TAF_RUN_E2E)
├── pyproject.toml                    # Build config (PEP 517/518, single source of truth)
├── sonar-project.properties          # SonarQube scanner config
├── Dockerfile                        # Test runner container (Python 3.12 + Playwright)
├── docker-compose.yml                # Local dev services (taf + optional Selenium Grid)
├── .github/workflows/ci.yml         # CI: lint → test → contract → build → docker
└── LICENSE                           # LGPL-3.0
```

## Implementation Rules

1. **Read architecture and plan** (`docs/implementation-plan.md`) before implementing any task.
2. **Run lint + tests after every change**: `flake8 src/ --max-line-length=120 && mypy src/main/python/taf/ --ignore-missing-imports && PYTHONPATH=src/main/python pytest src/test/python/ut/ -v`
3. **Never import concrete plugins directly** in test code — use ServiceLocator or modeling layer.
4. **Plugin config in YAML** — never hardcode plugin selection in Python code.
5. **No hardcoded credentials, IPs, or tokens** — use config files or environment variables.
6. **Preserve existing tests** — never delete or weaken existing test assertions.
7. **Match existing patterns** — inspect neighboring files before creating new ones.
8. **Copyright header required** on all new `.py` files: `Copyright (c) 2017-2026 Wesley Peng`, LGPL-3.0.
