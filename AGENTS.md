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
│   │   │   └── mobileplugin.py       # MobilePlugin — mobile
│   │   ├── api/ui/                   # UI element abstractions (controls, patterns, support)
│   │   ├── api/svc/REST/             # REST client base class
│   │   ├── api/cli/                  # CLI client base class
│   │   ├── plugins/                  # CONCRETE implementations
│   │   │   ├── web/selenium/         # SeleniumPlugin (Selenium 4, headless)
│   │   │   ├── svc/requests/         # RequestsPlugin
│   │   │   ├── cli/paramiko/         # ParamikoPlugin
│   │   │   └── mobile/appium/        # AppiumPlugin
│   │   ├── conf/                     # config.yml + Configuration loader
│   │   ├── servicelocator.py         # Plugin DI container
│   │   └── utils/                    # Logger, YAMLData, ConnectionCache, traits
│   └── modeling/                     # High-level test models
│       ├── web/                      # Browser + typed web controls
│       ├── svc/                      # RESTClient
│       └── cli/                      # CLIRunner
│
├── src/test/python/
│   ├── ut/                           # Framework unit tests (42 tests)
│   └── bpt/                          # BDD/ATDD examples (Bing, httpbin)
│
├── docs/
│   ├── architecture.md               # Architecture deep-dive
│   └── implementation-plan.md        # Task tracker (T.1–T.9)
│
├── CLAUDE.md                         # AI agent conventions (this project)
├── AGENTS.md                         # Reference tables (this file)
├── README.md                         # Project overview
├── architecture-diagram.svg          # Multi-layer architecture (v1.0)
├── diagram.png                       # Original PyXTaf architecture (preserved)
├── pyproject.toml                    # Build config (PEP 517/518, single source of truth)
├── src/main/python/setup.py          # Legacy setup.py (reads requirements.txt)
├── src/main/python/setup.cfg         # Legacy metadata
├── src/main/python/requirements.txt  # Core deps (mirrors pyproject.toml[dependencies])
├── src/main/python/requirements-dev.txt  # Dev deps (mirrors pyproject.toml[dev])
├── .github/workflows/ci.yml         # CI: lint → test → build
└── LICENSE                           # LGPL-3.0
```

### Planned directories (T.1.3+)

These will be created as part of future tasks:

```
src/main/python/taf/
│   ├── foundation/api/plugins/
│   │   ├── wsplugin.py               # T.1.3: WSPlugin — WebSocket
│   │   └── llmplugin.py              # T.1.3: LLMPlugin — LLM judge
│   ├── foundation/plugins/
│   │   ├── web/playwright/           # T.1.3: PlaywrightPlugin (new default)
│   │   ├── svc/httpx/                # T.1.3: HttpxPlugin (async)
│   │   ├── ws/                       # T.1.3: WebSocketPlugin
│   │   └── llm/                      # T.1.3: LLMJudgePlugin
│   ├── modeling/
│   │   ├── ws/                       # T.1.4: WSClient
│   │   └── llm/                      # T.1.4: LLMJudge
│   └── chaos/                        # T.1.5: K8s chaos module
│
src/test/python/
    └── suites/agentic/               # T.2–T.8: Platform test suites
        ├── api/                      # T.2: REST + WebSocket API tests
        ├── ui/                       # T.3: Playwright UI tests
        ├── ai/                       # T.4: LLM-as-judge tests
        ├── bdd/                      # T.5: Gherkin + behave
        ├── chaos/                    # T.6: Chaos experiments
        ├── load/                     # T.7: Performance tests
        ├── security/                 # T.8: RBAC, auth tests
        ├── contract/                 # T.2: OpenAPI validation
        └── config/                   # Environment configs
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
