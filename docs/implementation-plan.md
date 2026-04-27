# Implementation Plan

## Overview

This plan covers the modernization of the PyXTaf framework into Agentic-TAF and
the implementation of comprehensive test suites for the Agentic QA Platform.

Tasks are ordered by dependency. Each task has acceptance criteria and a validation command.

---

## T.1 — Framework Foundation

### T.1.1 — Rename and Rebrand (Done)

- [x] Rename repo: uiXautomation → agentic-taf
- [x] Update README, LICENSE (LGPL-3.0), copyright headers (2017-2026)
- [x] Package name: PyXTaf → Agentic-TAF, version: 0.5.1.0 → 1.0.0
- [x] Architecture diagram (SVG), CLAUDE.md, AGENTS.md
- [x] setup.cfg: Python >=3.12

### T.1.2 — Modernize Core (Python 3.12+) (Done)

- [x] Remove Python 2 compat: `__metaclass__` → `metaclass=`, `super(Cls, self)` → `super()`, `imp` → `importlib.util`, Py2 urlparse branches removed
- [x] Add type hints to ServiceLocator, Configuration, Client, plugin interfaces (mypy passes on 9 core files)
- [x] Create `pyproject.toml` with optional dependency groups (playwright, httpx, websocket, llm, dev)
- [x] Update `requirements.txt`: dropped `enum34`; added `selenium>=4.20`, `Appium-Python-Client>=4.0`
- [x] Configuration env var overrides: `TAF_PLUGIN_<NAME>_<KEY>` overrides YAML config
- [x] Fix `yaml.load()` → `yaml.full_load()` for custom `!YAMLData` tag support
- [x] Fix bare `except:` → `except Exception:` (7 instances in Selenium plugin + elementfinder)
- [x] Add `noqa: F401` to 25 `__init__.py` files with intentional re-exports
- [x] Fix bpt test files: Py3 syntax (`super()`, `class Foo:`, `except Exception:`)
- [x] Selenium 4 migration: `find_elements_by_*` → `find_elements(By, value)`, `Service`-based driver creation, headless support, deprecated `desired_capabilities` → `options`
- [x] SSHClient: decode stdout/stderr bytes → str for Python 3 compatibility
- [x] Mock external network calls (httpbin.org) in unit tests for CI reliability
- [x] Add 29 new unit tests: Configuration env overrides (6), Client codec/init (14), Plugin metaclass (9)
- [x] Enable browser tests (Chrome headless, inline data: URI) and SSH tests (key-based auth)
- [x] All tests pass: 42 collected, 42 passed, 0 skipped
- [x] CI: SSH setup for CLI tests, `python -m build` for wheel (replaces deprecated `setup.py bdist_wheel`)

**Validation**: `flake8 src/ && mypy src/main/python/taf/ --ignore-missing-imports && pytest src/test/python/ut/ -v`

### T.1.3 — New Plugin Interfaces + Implementations (Done)

| Plugin | Interface | Implementation | Deps |
|--------|-----------|----------------|------|
| Web (alt) | `WebPlugin` (existing) | `PlaywrightPlugin` | `playwright` |
| REST (alt) | `RESTPlugin` (existing) | `HttpxRESTPlugin` | `httpx` |
| WebSocket | `WSPlugin` (new) | `WebSocketPlugin` | `websockets` |
| LLM Judge | `LLMPlugin` (new) | `LLMJudgePlugin` | `langchain-anthropic` |

- [x] WSPlugin + LLMPlugin interfaces in `api/plugins/`
- [x] Base client classes: `api/ws/client.py` (connect/send/receive/close), `api/llm/client.py` (evaluate/score, 5-dimension rubric)
- [x] HttpxRESTPlugin: `plugins/svc/httpx/` — httpx.Client wrapper, implements full REST interface
- [x] WebSocketPlugin: `plugins/ws/websocket/` — websockets sync client
- [x] LLMJudgePlugin: `plugins/llm/judge/` — ChatAnthropic-based scoring with JSON parse
- [x] PlaywrightPlugin: `plugins/web/playwright/` — browser + 4 controls (Button, Edit, Link, Text) + ElementFinder
- [x] Modeling wrappers: `modeling/ws/WSClient`, `modeling/llm/LLMJudge`
- [x] config.yml: websocket + llm entries (enabled: False, defaults unchanged)
- [x] 47 new unit tests (89 total), all pass
- [x] mypy clean on 141 source files

**Validation**: `pytest src/test/python/ut/ -v` — all plugin discovery and basic operations pass

### T.1.4 — Modeling Layer Extensions (Done)

- [x] LLMClient refactored for provider agnosticism:
  - `provider='openai'` (default): uses `langchain-openai` ChatOpenAI — works with OpenAI, OpenRouter, local LLMs (Ollama, vLLM), SSO endpoints
  - `provider='anthropic'`: uses `langchain-anthropic` ChatAnthropic
  - Configurable via `TAF_LLM_PROVIDER` env var, `base_url`, `api_key` kwargs
  - Lazy imports — only loads the selected provider's SDK
  - Removed hard `ChatAnthropic` coupling from T.1.3
- [x] WSClient enhanced: `collect()` (batch receive), `collect_text()` (concatenate stream), `send_and_receive()` (request-response)
- [x] LLMJudge enhanced: `assert_quality()` with configurable `overall_threshold`, `dimension_thresholds`, `fail_any_below` floor — raises `AssertionError` with details on failure
- [x] pyproject.toml: `llm` group now uses `langchain-openai` (default); separate `llm-anthropic` and `llm-all` groups
- [x] 20 new unit tests (109 total); LLM tests cover both OpenAI and Anthropic providers
- [x] Validation: flake8 0, mypy 0 (141 files), pytest 109 passed

### T.1.5 — Chaos Plugin (Done)

Follows the same plugin architecture as REST, WebSocket, LLM, etc.
No standalone `taf/chaos/` module — chaos is a first-class plugin.

- [x] ChaosPlugin interface (`api/plugins/chaosplugin.py`) + base client (`api/chaos/client.py`)
- [x] Fault definitions: `PodKill`, `NetworkPartition`, `ResourcePressure`, `DNSFailure`, `FluxSuspend`
- [x] Probe definitions: `HttpHealthProbe`, `K8sReadyProbe`, `PrometheusProbe`
- [x] K8sChaosClient (`plugins/chaos/k8s/`): kubernetes Python client, pod delete, network policy, Flux suspend/resume
- [x] K8sChaosPlugin: ServiceLocator-discoverable, `config.yml` entry (enabled: False)
- [x] ChaosRunner modeling (`modeling/chaos/`): `run_experiment()` lifecycle, `assert_resilient()` with retry/timeout
- [x] Optional dep: `kubernetes>=31.0` in `pyproject.toml[chaos]`
- [x] 33 new unit tests (142 total); K8s tests skipUnless kubernetes installed
- [x] Validation: flake8 0, mypy 0 (152 files), pytest 142 passed

### T.1.6 — CI Skeleton (Done)

- [x] Enhanced `.github/workflows/ci.yml`:
  - JUnit XML output (`--junitxml=reports/unit-tests.xml`)
  - Coverage reporting (`--cov=taf --cov-report=xml:reports/coverage.xml`)
  - Upload test results + coverage as artifacts (`actions/upload-artifact@v4`)
  - `pytest-cov` added to `requirements-dev.txt` and `pyproject.toml[dev]`
- [x] Created `Jenkinsfile` at repo root:
  - Active stages: Install → Lint (parallel flake8/mypy) → Unit Tests → Build Wheel
  - Stub stages (disabled): API Tests → UI Tests → BDD → AI → Chaos → Load → Report
  - JUnit + coverage artifact archival in post steps

**Validation**: PR triggers GitHub Actions; lint + unit tests + coverage pass

---

## T.2 — API Tests (Done)

Target: 19 agent REST endpoints on preprod (via kubectl port-forward).

- [x] Created `suites/agentic/config/preprod.yml` with agent base URL + auth roles
- [x] Created `suites/agentic/conftest.py` with shared fixtures (config, agent_url, auth_headers)
- [x] T.2.1 — Contract tests (4 tests):
  - [x] OpenAPI schema stored as `contract/schemas/openapi.json` (18KB, 19 paths)
  - [x] Schema validity + endpoint existence checks
  - [x] All documented GET paths respond with non-5xx
  - [x] Live schema matches stored schema
- [x] T.2.2 — Functional API tests (13 tests):
  - [x] Health endpoint: status, components, LLM routing (3 tiers)
  - [x] LLM models: list, required fields
  - [x] Reporting: test-results, summary, reports, environments, flaky-tests, sonarqube
  - [x] Auth: invalid role → 400
  - [x] Metrics: Prometheus endpoint
- [x] T.2.3 — State machine tests (4 tests):
  - [x] List reservations
  - [x] Create → get → extend → release lifecycle (k8s)
  - [x] Nonexistent reservation → 400
  - [x] Release nonexistent → 400
- [x] All 21 E2E tests pass against live preprod (via kubectl port-forward)
- [x] All 142 unit tests still pass

**Validation**: `AGENT_BASE_URL=http://localhost:18000 pytest src/test/python/suites/agentic/api/ -v -m e2e`

---

## T.3 — UI Automation (Playwright) (Done)

Page Objects + Playwright headless E2E tests against live dashboard.

- [x] Page Objects: LoginPage (Ant Design form + select), DashboardPage, ChatPage, EnvironmentsPage
- [x] UI conftest.py: Playwright browser session fixture, page fixture with auto-navigation
- [x] Login flow (2 tests): login page visible, dev login → dashboard loaded
- [x] Navigation (3 tests): chat, environments, all 6 pages via nav sidebar
- [x] Dashboard (2 tests): dashboard loads with heading, no error state
- [x] Responsive layout (3 tests): desktop 1920, tablet 1366, mobile 375
- [x] preprod.yml updated with dashboard base URL
- [x] All 10 E2E UI tests pass against live preprod dashboard v0.9.1

**Validation**: `DASHBOARD_BASE_URL=http://localhost:18080 pytest src/test/python/suites/agentic/ui/ -v -m e2e`

---

## T.4 — AI-Specific Tests (Done)

Uses shared `api_client` fixture (ServiceLocator → HttpClient) to send
chat messages. Tests gracefully skip if agent LLM backend is unavailable.

Uses two framework plugins via ServiceLocator:
  - HttpClient (api_client fixture) for agent chat API calls
  - LLMClient (llm_judge fixture) for rubric-based response evaluation

- [x] T.4.1 — LLM-as-judge evaluation (3 tests): greeting quality, status query accuracy, provision completeness — uses `LLMJudge.assert_quality()` with 5-dimension rubric (accuracy, completeness, relevance, clarity, safety)
- [x] T.4.2 — Response quality (2 tests): thread_id presence, non-empty response
- [x] T.4.3 — Tool selection (1 test): greeting no infrastructure tools
- [x] T.4.4 — Adversarial (3 tests): prompt injection, secret extraction, hallucination
- [x] T.4.5 — Model fallback (2 tests): agent responds with available tier, 3 tiers configured
- [x] AI conftest.py: env override → ServiceLocator → LLMJudgePlugin → LLMClient, validated with assert
- [x] All 11 AI tests pass (or skip gracefully if LLM unavailable / langchain not installed)

**Validation**: `AGENT_BASE_URL=http://localhost:18000 pytest src/test/python/suites/agentic/ai/ -v -m ai`

---

## T.5 — BDD/ATDD (behave) (Done — PR #42 + follow-ups)

Uses HttpClient via ServiceLocator in behave `environment.py` (same chain as T.2).

- [x] `environment_provisioning.feature` (3 scenarios): list reservations, create K8s, invalid role
- [x] `chat_interaction.feature` (2 scenarios): greeting, status query (graceful on LLM down)
- [x] `llm_routing.feature` (2 scenarios): 3 LLM tiers configured, models have required fields
- [x] `environment_lifecycle.feature` (3 scenarios): provision → status → release lifecycle (added in follow-up)
- [x] Step definitions: provisioning_steps.py, chat_steps.py, llm_routing_steps.py, lifecycle_steps.py
- [x] environment.py: ServiceLocator → HttpxRESTPlugin → HttpClient, with assert validation
- [x] All 10 scenarios across 4 feature files pass against live preprod

**Validation**: `AGENT_BASE_URL=http://localhost:18000 behave src/test/python/suites/agentic/bdd/features/`

---

## T.6 — Chaos Engineering (Done)

Uses K8sChaosPlugin resolved via ServiceLocator + ChaosRunner from modeling layer.

- [x] conftest.py: env override → ServiceLocator → K8sChaosPlugin → K8sChaosClient, validated with assert
- [x] Agent pod kill → K8s readiness probe recovery (ChaosRunner.assert_resilient with retry)
- [x] Agent pod kill → HTTP health probe recovery
- [x] Flux suspend → agent health still responds (skip if kustomization unavailable)
- [x] Concurrent reservations (5 parallel) → no server errors/deadlocks
- [x] 4 chaos experiments pass against live preprod

**Validation**: `KUBECONFIG=... AGENT_BASE_URL=http://localhost:18000 pytest src/test/python/suites/agentic/chaos/ -v -m chaos --timeout=600`

---

## T.7 — Load & Performance (Done)

Uses shared api_client fixture (ServiceLocator → HttpClient) for HTTP tests.
WebSocket tests use websockets library directly. Scaled-down parameters for CI
(10s duration, 10 concurrent WS, 5 chat requests); full runs use higher values.

- [x] T.7.1 — API throughput: sustained GET /api/v1/reservations at target RPS, p95 < 2s, error rate < 5%
- [x] T.7.2 — WebSocket scale: concurrent connections each send/receive a message, 80%+ success
- [x] T.7.3 — Provision throughput: 10 parallel POST /reservations, all return non-5xx, cleanup after
- [x] T.7.4 — Chat latency: sequential POST /api/v1/chat, p95 < 15s for complete response
- [x] 4 load tests collected

**Validation**: `AGENT_BASE_URL=http://localhost:18000 pytest src/test/python/suites/agentic/load/ -v -m load --timeout=900`

---

## T.8 — Security Tests (Done)

- [x] Role enforcement (3 tests): viewer cannot POST (403), developer can create, invalid role (400)
- [x] Secret exposure scan (2 tests): regex patterns for GitHub PATs, API keys, private keys; no credentials in health/models/reporting
- [x] Header injection (3 tests): SQL injection, XSS, oversized headers — all return <500
- [x] All 8 E2E security tests pass against live preprod

**Validation**: `AGENT_BASE_URL=http://localhost:18000 pytest src/test/python/suites/agentic/security/ -v -m e2e`

---

## T.9 — Reporting & CI Integration (Done)

Full CI pipeline activated with reporting integrations.

- [x] T.9.1 — JUnit XML → OpenSearch: `push_results.py` parses JUnit XML files, bulk-indexes to OpenSearch `test-results` index. Also supports agent reporting API (`POST /api/v1/reporting/test-results`).
- [x] T.9.2 — Coverage → SonarQube: `sonar-project.properties` configured (project key, source paths, coverage report path). Jenkins Report stage runs `sonar-scanner` when `SONAR_HOST_URL` + `SONAR_TOKEN` are set.
- [x] T.9.3 — AI traces → LangFuse: LLM-as-judge tests use LangFuse callback handler when `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` are set (via langchain integration).
- [x] T.9.4 — Jenkins pipeline (full): All 11 stages active (Install → Lint → Unit Tests → Build → API → Security → UI → BDD → AI → Chaos → Load → Report). E2E stages gated by `TAF_RUN_E2E=true` parameter. JUnit results collected per stage. Report stage pushes to OpenSearch + SonarQube.
- [x] T.9.5 — GitHub Actions (PR): lint + unit + contract validation + build. Docker image build on tag push. API contract job validates stored OpenAPI schema on PRs.
- [x] Dockerfile: Python 3.12-slim + Playwright chromium, all optional deps. `ENTRYPOINT ["pytest"]`.
- [x] docker-compose.yml: `taf` service (test runner) + optional Selenium Grid. `docker compose run taf` runs unit tests.
- [x] sonar-project.properties: project key, source/test paths, coverage report

**Validation**: Jenkins pipeline lint+unit stages pass; GitHub Actions CI passes; `docker compose run --profile test taf` works

---

## T.10 — LLM-as-Judge E2E Testing Expansion (Done)

Expands the existing 4-layer LLM-judge stack (T.1.3, T.1.4) and the AI suite
(T.4) to cover **ground-truth anchored evaluation** — the highest-value
LLM-judge pattern that uses the platform's deterministic REST APIs as ground
truth for evaluating chat-agent natural-language responses.

Task ordering (rubrics → fixture promotion → tests → docs) was chosen to
keep blast radius small at each step; see
`agentic-qa-platform/.windsurf/plans/phase-9-test-automation-framework.md`
T.10 for the detailed rationale.

- [x] **T.10.1** — Domain rubrics + per-call override:
  `Client.GROUND_TRUTH_RUBRIC`, `DEGRADED_MODE_RUBRIC`, `ADVERSARIAL_RUBRIC`
  class constants on `taf/foundation/api/llm/client.py`. New `rubric`
  parameter on `LLMJudge.assert_quality()` temporarily swaps `self.rubric`
  for the call (try/finally restore — safe under exception). 3 new unit
  tests in `test_modeling_extensions.py` (per-call swap, restoration after
  exception, constants accessible and distinct).
- [x] **T.10.2** — Promoted `llm_judge` and `llm_client_cls` fixtures from
  `ai/conftest.py` to shared `agentic/conftest.py`. Added two new fixtures:
  - `llm_judge_optional` — returns `None` if langchain unavailable
    (opt-in pattern for non-AI suites: chaos, security, BDD)
  - `chat_and_judge` — composite that sends a chat message and optionally
    judges the response, returning `(data, scores | None)`
  AI suite preserves skip-on-missing semantics by depending on `llm_judge`
  (which delegates to `llm_client_cls` which calls `pytest.skip()`).
  `ai/conftest.py` is now minimal (re-imports from parent).
- [x] **T.10.3** — New `suites/agentic/ai/test_e2e_quality.py` with two
  test classes (5 E2E tests total):
  - `TestGroundTruthAccuracy` (3 tests): health, reservations, LLM models
    — chat response evaluated against deterministic API ground truth using
    `GROUND_TRUTH_RUBRIC` and accuracy thresholds (≥3.5–4.0).
  - `TestMultiTurnCoherence` (2 tests): provision-then-status, team
    retention — verifies thread-id-based context retention with relevance
    + accuracy thresholds.
  Re-uses `_chat()` and `_skip_if_llm_unavailable()` helpers from
  `test_ai.py`.
- [x] **T.10.4** — README, CLAUDE.md, AGENTS.md, architecture.md updated
  to reflect 274 unit tests / 16 AI tests / 63 total E2E and the new
  shared-fixture pattern.

**Validation**: `flake8 src/ --max-line-length=120` clean; `mypy
src/main/python/taf/ --ignore-missing-imports` 152 files clean;
`pytest src/test/python/ut/` — **274 passed**.

**Future work (deferred to follow-up PRs)** — see phase-9 plan F.1-F.4:
chaos post-recovery quality, security adversarial judge, BDD quality step,
config + CI marker.

---

## Implementation Order

| Phase | Tasks | Priority |
|-------|-------|----------|
| T.1 | Framework foundation (T.1.1–T.1.6) | P0 |
| T.2 | API tests | P0 |
| T.3 | UI automation | P0 |
| T.9 | CI integration | P0 |
| T.4 | AI-specific tests | P1 |
| T.5 | BDD scenarios | P1 |
| T.6 | Chaos engineering | P1 |
| T.7 | Load & performance | P2 |
| T.8 | Security tests | P2 |
| T.10 | LLM-judge E2E expansion (T.10.1-T.10.4) | P1 |

**Critical path**: T.1 → T.2 → T.4 (framework → API → AI tests)
