# OHDSI WebAPI Client Architecture Guide

## Service-Oriented Architecture
The client follows a service pattern with domain-specific modules:
- `WebApiClient` acts as the main facade exposing service instances via properties (`client.vocab`, `client.cohorts`, etc.)
## Architecture & Design Patterns

- Each service in `src/ohdsi_webapi/services/` encapsulates a logical domain (vocabulary, concept sets, cohorts, sources, info, jobs)
- Services receive an `HttpExecutor` instance for consistent HTTP handling with retry logic and auth injection

## Key Data Flow Patterns

### WebAPI Response Normalization
WebAPI returns inconsistent field naming (uppercase vs camelCase). The VocabularyService demonstrates the normalization pattern:
```python
# In vocab.py: _normalize_concept_payload() maps CONCEPT_ID -> conceptId
# Use this pattern when adding new endpoints that return Atlas-style uppercase fields
```

### Async Job Polling
Cohort generation follows the async pattern - see `CohortService.poll_generation()`:
1. Initiate job via POST endpoint
2. Poll status endpoint until terminal state (`COMPLETED`, `FAILED`, `STOPPED`)
3. Handle timeouts with `JobTimeoutError`

### Expression Resolution Pattern
Concept sets use a compact expression → expanded resolution pattern:
- Store lightweight expressions with seed concepts + flags
- Resolve to concrete concept lists via `/resolve` endpoints
- Use this for any hierarchical expansion needs

## Development Workflow

### Testing Strategy
- **Unit tests**: `tests/unit/` with `respx` mocks for fast isolated testing
- **Live tests**: `tests/live/` against public demo (read-only, env-gated via `INTEGRATION_WEBAPI=1`)
- Run unit: `poetry run pytest tests/unit`
- Run live: `INTEGRATION_WEBAPI=1 OHDSI_WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI poetry run pytest tests/live`

### Error Handling Convention
All services raise `WebApiError` subclasses with structured context:
```python
# Include endpoint, status_code, and raw payload for debugging
raise NotFoundError("Concept not found", status_code=404, endpoint="/vocabulary/concept/999", payload=response_data)
```

### Model Design
Pydantic models in `src/ohdsi_webapi/models/` are domain-grouped:
- Keep expressions as raw `dict` types (complex nested structures)
- Use Optional fields liberally - WebAPI versions vary in returned fields
- Add helper methods for common transformations, not business logic

## Integration Points

### Authentication
Pluggable via `AuthStrategy` base class in `auth/`:
- `BasicAuth` and `BearerToken` implementations provided
- Pass to `WebApiClient(auth=strategy)` - headers injected per request

### HTTP Layer
`HttpExecutor` centralizes:
- Connection pooling (httpx client reuse)
- Retry with exponential backoff (tenacity)
- Response parsing (JSON vs text handling)
- Error translation to domain exceptions

### External Dependencies
- **httpx**: HTTP client with sync support (HTTP/2 enabled)
- **pydantic**: Data validation and parsing
- **tenacity**: Retry logic for network resilience
- **respx**: HTTP mocking for tests

## Project-Specific Conventions

### Service Method Patterns
- `list()` returns list of domain objects
- `get(id)` returns single object or raises
- Bulk operations use `_many` suffix: `resolve_many()`
- Export methods return raw text/JSON strings, not parsed objects

### File Organization
```
src/ohdsi_webapi/
├── __init__.py
```

### Environment Configuration
- Use `poetry.toml` for local venv (`in-project = true`)
- Integration tests controlled by `INTEGRATION_WEBAPI` and `OHDSI_WEBAPI_BASE_URL`
- No config files - prefer constructor parameters and env vars

## Critical Implementation Details

### Uppercase Field Handling
WebAPI inconsistently returns `CONCEPT_ID` vs `conceptId`. Always implement field normalization in service methods when working with Atlas-exported data.

### Context Manager Support
`WebApiClient` supports context manager pattern:
```python
with WebApiClient(url) as client:
    # Automatically calls client.close()
```

### Type Safety
Full mypy strict mode enabled. Use Union types for WebAPI's flexible response formats, but provide typed service method signatures.
