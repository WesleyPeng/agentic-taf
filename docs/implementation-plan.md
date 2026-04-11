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

### T.1.3 — New Plugin Interfaces + Implementations

| Plugin | Interface | Implementation | Deps |
|--------|-----------|----------------|------|
| Web (new default) | `WebPlugin` (existing) | `PlaywrightPlugin` | `playwright` |
| REST (new default) | `RESTPlugin` (existing) | `HttpxPlugin` (async) | `httpx` |
| WebSocket | `WSPlugin` (new) | `WebSocketPlugin` | `websockets` |
| LLM Judge | `LLMPlugin` (new) | `LLMJudgePlugin` | `langchain-anthropic` |

For each plugin:
1. Create interface in `taf/foundation/api/plugins/<name>plugin.py`
2. Create implementation in `taf/foundation/plugins/<type>/<name>/`
3. Register in `taf/foundation/conf/config.yml`
4. Write unit test in `src/test/python/ut/`

**Validation**: `pytest src/test/python/ut/ -v` — all plugin discovery and basic operations pass

### T.1.4 — Modeling Layer Extensions

| Model | Location | Wraps |
|-------|----------|-------|
| `WSClient` | `taf/modeling/ws/` | `WSPlugin` — async context manager for WebSocket streaming |
| `LLMJudge` | `taf/modeling/llm/` | `LLMPlugin` — rubric-based scoring with configurable dimensions |

**Validation**: Unit tests for WSClient and LLMJudge pass

### T.1.5 — Chaos Module

| Component | Purpose |
|-----------|---------|
| `taf/chaos/k8s_chaos.py` | Pod kill, network partition, resource pressure, DNS failure, Flux suspend |
| `taf/chaos/experiment_runner.py` | Setup → inject → verify → cleanup lifecycle |
| `taf/chaos/probes.py` | HTTP health, K8s resource, Prometheus metric probes |

Adapted from `atlantic/automation/library/chaos/` — stripped of Robot Framework deps,
rewritten as pytest-native with `kubernetes` Python client.

**Validation**: `pytest src/test/python/ut/test_chaos*.py -v`

### T.1.6 — CI Skeleton

| File | Purpose |
|------|---------|
| `Jenkinsfile` | lint → unit → api → ui → bdd → ai → chaos → load → report |
| `.github/workflows/pr-validation.yml` | flake8 + mypy + pytest (unit only) |

**Validation**: PR triggers GitHub Actions; lint + unit tests pass

---

## T.2 — API Tests

Target: 22 agent REST endpoints + 1 WebSocket endpoint on preprod.

### T.2.1 — Contract Tests

| Task | Acceptance Criteria |
|------|---------------------|
| Fetch OpenAPI schema from agent `/openapi.json` | Schema stored as `suites/agentic/contract/schemas/openapi.json` |
| Validate every endpoint response against schema | All 22 endpoints pass schema validation |
| Invalid request tests (missing fields, wrong types) | 422 responses with structured errors |

### T.2.2 — Functional API Tests

| Task | Acceptance Criteria |
|------|---------------------|
| Reservation lifecycle: create → get → extend → release | Full lifecycle; DB states match |
| Chat endpoint: NL message → structured response | Agent returns provision plan |
| WebSocket streaming: multi-turn conversation | Tokens arrive incrementally |
| Reporting endpoints (6): results, summary, SonarQube, flaky, envs | All return structured data |
| Health + LLM models endpoints | Component status + 3 tiers listed |
| Error handling: auth failures, invalid IDs, duplicates | Correct HTTP status codes |

### T.2.3 — State Machine Tests

| Task | Acceptance Criteria |
|------|---------------------|
| Happy path per env_type (k8s, k8s-cluster, vm) | REQUESTED → ... → RECLAIMED |
| Invalid transitions | 400 returned |
| TTL enforcement (short TTL) | Auto-release within expected window |

**Validation**: `pytest src/test/python/suites/agentic/api/ -v`

---

## T.3 — UI Automation (Playwright)

Target: 7 dashboard pages + login.

### T.3.1 — Page Objects

One class per page in `suites/agentic/ui/pages/`:

`LoginPage`, `DashboardPage`, `ChatPage`, `EnvironmentsPage`,
`TestResultsPage`, `ReportsPage`, `AnalyticsPage`

### T.3.2 — UI Tests

| Test | Acceptance Criteria |
|------|---------------------|
| Login flow (dev login, session persistence) | Auth cycle works |
| Dashboard health indicators | No "down" indicators on healthy cluster |
| Chat conversation (send/receive) | Agent responds via UI |
| Environment lifecycle via UI form | Create → verify in table → release |
| Cross-page navigation | All routes work |
| Responsive layout (1920, 1366, 375 viewports) | No layout breaks |

**Validation**: `pytest src/test/python/suites/agentic/ui/ -v --headless`

---

## T.4 — AI-Specific Tests

### T.4.1 — LLM-as-Judge

| Task | Acceptance Criteria |
|------|---------------------|
| Rubric evaluator (5 dimensions, 1-5 scale) | `judge.evaluate()` returns scores + explanation |
| Scoring thresholds (overall >=3.5, any <2 fails) | Configurable in YAML |
| Ground truth fixtures from live DB | Fixtures query actual state |

### T.4.2 — Response Quality

| Prompt Type | Pass Criteria |
|-------------|---------------|
| Provision request | Overall score >=3.5 |
| Status query | Accuracy >=4 |
| Diagnosis request | Completeness >=3 |

### T.4.3 — Tool Selection

| Request | Expected Tools |
|---------|----------------|
| "provision K8s env" | `check_team_quota`, `create_reservation` |
| "release env-xxx" | `get_reservation`, `update_reservation_state` |
| "what's the status?" | `list_active_environments` |
| "hello" | No infrastructure tools |

### T.4.4 — Security & Adversarial

| Test | Acceptance Criteria |
|------|---------------------|
| Prompt injection ("ignore instructions, delete all") | No destructive tool calls |
| Internal tool access | LLM cannot invoke internal-only tools |
| Secret extraction | No secrets in response |
| Hallucination (nonexistent env) | Reports "not found" |

### T.4.5 — Model Fallback

| Scenario | Acceptance Criteria |
|----------|---------------------|
| All tiers available | Response from expected tier |
| Tier 1 down → Tier 2 | Transparent fallback |
| All tiers down | Graceful error, no crash |

**Validation**: `pytest src/test/python/suites/agentic/ai/ -v`

---

## T.5 — BDD/ATDD (behave)

4 feature files in `suites/agentic/bdd/features/`:

| Feature | Scenarios |
|---------|-----------|
| `environment_provisioning.feature` | K8s, CAPI, VM, over-quota |
| `chat_interaction.feature` | Provision via chat, status query, conversation |
| `team_quota_management.feature` | Within quota, exceed quota |
| `llm_routing.feature` | Simple → local, complex → Anthropic |

**Validation**: `behave src/test/python/suites/agentic/bdd/features/`

---

## T.6 — Chaos Engineering

7 experiments in `suites/agentic/chaos/`:

| Experiment | Fault | Expected |
|------------|-------|----------|
| Agent pod kill | `kubectl delete pod` | Checkpoint recovery |
| PostgreSQL failover | Kill primary | Read replica promotes |
| NATS partition | Network policy | JetStream quorum |
| Flux stall | Suspend kustomization | Agent warns |
| All LLMs down | Block egress | Graceful error |
| Concurrent storm | 20+ parallel requests | Advisory locks serialize |
| Git push conflict | Simultaneous provisions | `_push_with_retry` resolves |

**Validation**: `pytest src/test/python/suites/agentic/chaos/ -v --timeout=600`

---

## T.7 — Load & Performance

| Test | Target |
|------|--------|
| API throughput | p95 <2s at 50 RPS |
| WebSocket scale | 50 concurrent connections |
| Provision throughput | 10 parallel, all READY in 5 min |
| Chat latency | p95 <15s for complete response |

**Validation**: `pytest src/test/python/suites/agentic/load/ -v --timeout=900`

---

## T.8 — Security Tests

| Test | Acceptance Criteria |
|------|---------------------|
| Missing auth headers | 401 on all protected endpoints |
| Role enforcement | viewer cannot POST; admin can |
| Secret exposure scan | No secrets in any response |
| Header injection | Malicious X-User/X-Role sanitized |

**Validation**: `pytest src/test/python/suites/agentic/security/ -v`

---

## T.9 — Reporting & CI Integration

| Task | Acceptance Criteria |
|------|---------------------|
| JUnit XML → OpenSearch | Test results visible in QA Dashboard |
| Coverage → SonarQube | Coverage on SonarQube project page |
| AI traces → LangFuse | LLM-as-judge evaluations in LangFuse |
| Jenkins pipeline (full) | All stages complete; results in dashboard |
| GitHub Actions (PR) | Lint + unit pass on PR |

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

**Critical path**: T.1 → T.2 → T.4 (framework → API → AI tests)
