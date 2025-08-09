High-level phased plan:

1. Scope & Requirements
- Define supported WebAPI versions and minimum endpoints (sources, vocab/concepts, concept sets (CRUD + resolve), cohorts (CRUD + generate + status + results), jobs, characterization, Achilles results).
- Decide sync vs async (recommend both).
- Identify auth modes to support (no auth, basic auth, bearer token, keycloak/OAuth2 password + client credentials).

2. API Design
- Core client class (WebApiClient) holding base_url, session, auth, retry, timeout.
- Resource-specific service objects or modular subpackages (client.cohorts, client.vocab, etc.).
- Data models via Pydantic for request/response schemas (versioned namespace).
- Consistent exception hierarchy (e.g., WebApiError -> HTTPError, NotFound, JobTimeout, ValidationError).
- Pagination & streaming abstractions (iterator returning domain models).
- Job polling helper (exponential backoff, cancellation support).

3. Technical Foundations
- Use httpx (sync + async unified) or requests + aiohttp; prefer httpx.
- Implement retry (HTTP 429/5xx) with backoff (tenacity or custom).
- Add optional caching (ETag/Last-Modified; in-memory + pluggable cache interface).
- Add rate limiting (token bucket) optional.

4. Features (MVP)
- Connection test (GET /WebAPI/info).
- List sources (/WebAPI/source/sources).
- Vocab: concept lookup (/concept/{id}), search (/vocabulary/search), descendants/ancestors.
- Concept set: CRUD + export expression + resolve to ids & included concepts.
- Cohort definitions: CRUD, generate (POST generate), poll job, fetch inclusion stats, fetch counts.
- Job management: generic poller for /job/{id} status.
- Error translation: Parse WebAPI error body; map to exceptions.

5. Advanced Features (Phase 2)
- Cohort characterization (spec upload + execution retrieval).
- Pathways, Incidence Rate, Estimation, Prediction specs.
- Achilles results abstractions.
- Bulk operations (batch concept retrieval with concurrency).
- CLI wrapper (e.g., webapi-cli cohorts generate ...).
- Dataset export helpers (convert to pandas DataFrame).

6. Code Organization
```
package/
init.py (expose version, main client)
config.py
auth.py (BasicAuth, TokenAuth, OAuthClient)
http.py (HttpExecutor, retry, caching)
models/ (pydantic schemas grouped by domain)
services/ (cohorts.py, vocab.py, concept_sets.py, jobs.py)
exceptions.py
utils/ (poller, pagination)
cli/ (optional click or typer)
tests/
unit/ (mocked httpx)
integration/ (docker-compose optional later)
contract/ (recorded cassettes via vcrpy)
```

7. Testing Strategy
- Use pytest.
- Mock HTTP using respx for httpx.
- Contract tests against a specific WebAPI version container (GitHub Actions service container).
- Fixture for spinning test WebAPI (docker image).
- Add type checking (mypy), linting (ruff), formatting (black), import sorting (ruff/isort).


8. Python conventions, versioning & Compatibility
- Python 3.11 or higher
- Poetry for packaging. 
- Numpy-style docstrings. 
- Typing. 
- Semantic versioning.
- Track WebAPI schema differences—expose .server_version.
- Capability detection (feature flags if endpoints missing).


9. Auth & Security
- Pluggable token refresh (OAuth2).
- Never log secrets; structured logging with redaction.
- Optional TLS certificate pinning (requests adapters / httpx verify param).
- Support custom headers injection.


10. Performance
- Connection pooling (httpx client reuse).
- Optional async bulk fetch (gather).
- Rate limiter around high-volume endpoints.


11. Documentation
- Auto-generate API reference from docstrings (mkdocs + mkdocs-material).
- Quickstart, examples (sync + async, cohort generate, concept set resolve).
- Version matrix (library vs WebAPI).
- Contributing guide: dev setup, tests, release process.


12. Tooling & Packaging
pyproject.toml (PEP 621; dependencies: httpx[phttp2], pydantic, tenacity, typing-extensions).
Optional extras: cli, pandas.
Pre-commit hooks (black, ruff, mypy).
GitHub Actions workflows: lint, test (unit + contract), build, publish (on tag).
Code coverage (coverage.py + Codecov).


13. Error Handling & DX
Rich exceptions with .status_code, .endpoint, .payload.
Graceful timeouts configurable (connect/read).
Provide trace logging option (debug HTTP).


14. Release & Governance
LICENSE (Apache 2.0).
CODE_OF_CONDUCT, SECURITY.md, CONTRIBUTING.md.
Changelog (Keep a Changelog format).
Issue templates, PR template.
Roadmap Items
Pluggable serialization (raw dict or pydantic).
Add typed query builders (fluent DSL) later.
DataFrame export convenience in separate module to keep core lean.
Initial Implementation Order (practical)

Project scaffold + tooling (pyproject, lint, tests).
http layer + auth + exceptions.
Info & sources endpoints (prove architecture).
Vocabulary & concept retrieval.
Concept set CRUD + resolve.
Cohort CRUD + generation + job poller.
Documentation + examples.
Publish 0.1.0.