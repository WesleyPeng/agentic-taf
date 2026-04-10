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
│   │   │   ├── wsplugin.py           # WSPlugin — WebSocket (new)
│   │   │   └── llmplugin.py          # LLMPlugin — LLM judge (new)
│   │   ├── api/ui/                   # UI element abstractions (controls, patterns, support)
│   │   ├── api/svc/REST/             # REST client base class
│   │   ├── api/cli/                  # CLI client base class
│   │   ├── plugins/                  # CONCRETE implementations
│   │   │   ├── web/playwright/       # PlaywrightPlugin (new)
│   │   │   ├── web/selenium/         # SeleniumPlugin (existing)
│   │   │   ├── svc/httpx/            # HttpxPlugin (new)
│   │   │   ├── svc/requests/         # RequestsPlugin (existing)
│   │   │   ├── ws/                   # WebSocketPlugin (new)
│   │   │   ├── cli/paramiko/         # ParamikoPlugin (existing)
│   │   │   ├── mobile/appium/        # AppiumPlugin (existing)
│   │   │   └── llm/                  # LLMJudgePlugin (new)
│   │   ├── conf/                     # config.yml + Configuration loader
│   │   ├── servicelocator.py         # Plugin DI container
│   │   └── utils/                    # Logger, YAMLData, ConnectionCache, traits
│   ├── modeling/                     # High-level test models
│   │   ├── web/                      # Browser + typed web controls
│   │   ├── svc/                      # RESTClient
│   │   ├── cli/                      # CLIRunner
│   │   ├── ws/                       # WSClient (new)
│   │   └── llm/                      # LLMJudge (new)
│   └── chaos/                        # K8s chaos module (new)
│
├── src/test/python/
│   ├── ut/                           # Framework unit tests
│   ├── bpt/                          # BDD/ATDD examples (Bing, httpbin)
│   └── suites/agentic/              # Agentic QA Platform test suites
│       ├── api/                      # REST + WebSocket API tests
│       ├── ui/                       # Playwright UI tests + page objects
│       ├── e2e/                      # End-to-end provisioning flows
│       ├── bdd/                      # Gherkin + behave scenarios
│       ├── ai/                       # LLM-as-judge, tool selection, injection
│       ├── chaos/                    # Platform chaos experiments
│       ├── load/                     # Performance / throughput tests
│       ├── security/                 # RBAC, auth, secret tests
│       ├── contract/                 # OpenAPI schema validation
│       └── config/                   # preprod.yml, dev.yml, ci.yml
│
├── CLAUDE.md                         # AI agent conventions (this project)
├── AGENTS.md                         # Reference tables (this file)
├── README.md                         # Project overview + architecture diagram
├── architecture-diagram.svg          # Multi-layer architecture (v1.0)
├── diagram.png                       # Original PyXTaf architecture (preserved)
├── pyproject.toml                    # Build config (replaces setup.py + PyBuilder)
├── Dockerfile                        # Test runner container
└── docker-compose.yml                # Local dev services
```

## Implementation Rules

1. **Read architecture and plan** (`docs/architecture.md`, `docs/implementation-plan.md`) before implementing any task.
2. **Run lint + tests after every change**: `flake8 src/main/python/ src/test/python/ --max-line-length=120 && mypy src/main/python/taf/ --ignore-missing-imports && pytest src/test/python/ut/ -v`
3. **Never import concrete plugins directly** in test code — use ServiceLocator or modeling layer.
4. **Plugin config in YAML** — never hardcode plugin selection in Python code.
5. **No hardcoded credentials, IPs, or tokens** — use config files or environment variables.
6. **Preserve existing tests** — never delete or weaken existing test assertions.
7. **Match existing patterns** — inspect neighboring files before creating new ones.
8. **Copyright header required** on all new `.py` files: `Copyright (c) 2017-2026 Wesley Peng`, LGPL-3.0.
