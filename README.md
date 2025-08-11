# OHDSI WebAPI Client (Python)

Alpha-stage Python client for interacting with an OHDSI WebAPI instance.

## MVP Scope
- Info & health check
- Sources listing
- Vocabulary: concept lookup, search (basic), hierarchy (descendants)
- Concept Set: CRUD, expression export, resolve (included concepts)
- Cohort Definitions: CRUD, generate, job polling, inclusion stats, counts

## Install (development)
```bash
poetry install
```

(Ensure local venv is in-project: `.venv/` created via `poetry.toml`.)

## Environment Configuration
Copy the sample environment file and customize:
```bash
cp .env.sample .env
# Edit .env with your settings
```

The `.env` file is automatically loaded when you import the package. Key settings:
- `OHDSI_WEBAPI_BASE_URL`: Your WebAPI server URL
- `OHDSI_WEBAPI_AUTH_TOKEN`: Authentication token (optional)
- `OHDSI_CACHE_ENABLED`: Enable/disable caching (default: true)  
- `OHDSI_CACHE_TTL`: Cache TTL in seconds (default: 300)
- `OHDSI_CACHE_MAX_SIZE`: Maximum cache entries (default: 128)
- `INTEGRATION_WEBAPI`: Enable live integration tests (default: 0)

### Interactive Development
The `.env` file works seamlessly with Poetry and IPython:
```bash
# Environment variables are automatically loaded
poetry run ipython
poetry run python your_script.py
poetry run pytest
```

## Install (from PyPI - when published)
```bash
pip install ohdsi-webapi-client
```

## Quickstart
```python
from ohdsi_webapi import WebApiClient
import os

# Uses OHDSI_WEBAPI_BASE_URL from .env if set, otherwise explicit URL
base_url = os.getenv("OHDSI_WEBAPI_BASE_URL", "http://localhost:8080/WebAPI")
client = WebApiClient(base_url=base_url)

print(client.info.version())
for src in client.sources.list():
    print(src.sourceKey)
concept = client.vocab.get_concept(201826)  # Metformin
print(concept.conceptName)

# WebAPI endpoint-style aliases also supported:
domains = client.vocabulary.domains()  # Same as client.vocab.list_domains()
concept_sets = client.conceptset.list()  # Same as client.concept_sets.list()

# Build cohorts incrementally with counts at each step (async method)
import asyncio

async def build_cohort_example():
    diabetes_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")
    results = await client.cohorts.build_incremental_cohort(
        source_key="your_source",
        base_name="Diabetes Study", 
        concept_sets=[diabetes_cs],
        filters=[
            {"type": "gender", "gender": "male"},
            {"type": "age", "min_age": 40},
            {"type": "time_window", "concept_set_id": 0, "days_before": 730}
        ]
    )

    for i, (cohort, count) in enumerate(results):
        print(f"Step {i+1}: {count:,} patients - {cohort.name}")

# To run: asyncio.run(build_cohort_example())

client.close()
```

## API Design Philosophy

### REST Endpoint Mirroring
This client follows a **predictable naming convention** that mirrors the WebAPI REST endpoints, making it intuitive for developers familiar with the HTTP API:

| REST Endpoint | Python Method | Description |
|--------------|---------------|-------------|
| `/vocabulary/domains` | `client.vocabulary.domains()` | Get all domains |
| `/vocabulary/vocabularies` | `client.vocabulary.vocabularies()` | Get all vocabularies |
| `/vocabulary/concept/{id}` | `client.vocabulary.concept(id)` | Get a concept |
| `/vocabulary/concept/{id}/descendants` | `client.vocabulary.concept_descendants(id)` | Get child concepts |
| `/vocabulary/concept/{id}/related` | `client.vocabulary.concept_related(id)` | Get related concepts |

**Naming Convention:**
- **Base resources**: Use the plural noun (e.g., `vocabularies()`, `domains()`)
- **Sub-resources**: Use underscore notation (e.g., `concept_descendants()`, `concept_related()`)
- **Single items**: Use singular noun (e.g., `concept(id)`)

This approach tries to make the API self-documenting for developers who understand the underlying REST structure.


## Testing
### Unit tests (mocked, fast)
```bash
poetry run pytest
```
These use `respx` to mock HTTP endpoints.

### Live integration tests (public demo, read-only)
Disabled by default. To run:
```bash
export INTEGRATION_WEBAPI=1
export OHDSI_WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI
poetry run pytest tests/live -q
```
Only GET/read-only endpoints are exercised (concept lookup & search). Write operations are intentionally excluded to avoid mutating the shared demo server.

### Local full integration (future)
Spin up a local WebAPI + database (Docker) to safely test create/update/delete for concept sets and cohorts. (Compose file TBD.)

## Concept & Concept Sets Summary
- `client.vocab.get_concept(id)` fetches a single concept (handles uppercase Atlas-style keys).
- `client.vocab.search(query)` returns concepts matching text.
- `client.vocab.descendants(id)` navigates hierarchy.
- `client.concept_sets.create(name)` creates an empty concept set.
- Modify `concept_set.expression` (Atlas JSON structure) then `client.concept_sets.update(cs)`.
- `client.concept_sets.resolve(id)` expands expression to concrete included concepts.

## Additional Documentation
See the docs directory for deeper guides:
- [OHDSI Sources](docs/sources.md) - working with data sources and CDM databases  
- [Vocabulary & Concepts](docs/vocabulary.md) - concept lookup, search, and hierarchies
- [Finding Codes](docs/finding_codes.md) - techniques for discovering OMOP concept codes
- [Concept Sets](docs/concept_sets.md) - creating and managing concept collections
- [Cohorts](docs/cohorts.md) - cohort definition management and generation
- [Cohort Building](docs/cohort_building.md) - advanced cohort construction patterns
- [Supported Endpoints](docs/supported_endpoints.md) - which WebAPI endpoints are supported
- [Caching](docs/caching.md) - performance optimization with intelligent caching

## Roadmap
See `ROADMAP.md` (to be added).Planned:
- authentication.md – Auth strategies & configuration
- jobs.md – Asynchronous job polling patterns


## License
Apache 2.0
