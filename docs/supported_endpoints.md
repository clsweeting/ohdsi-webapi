# Supported WebAPI Endpoints

This page lists all OHDSI WebAPI endpoints currently supported by this Python client. The [official WebAPI documentation](http://webapidoc.ohdsi.org/index.html) shows hundreds of endpoints, but this client focuses on the core functionality needed for cohort building and vocabulary operations.

## Coverage Philosophy

This client prioritizes **cohort building workflows** and covers these key areas:
- Vocabulary & Concepts: Search and retrieve medical concepts
- Concept Sets: Create and manage reusable concept groups  
- Cohort Definitions: Define and generate patient cohorts
- Sources: List available data sources

**Not Currently Supported:**
- Atlas-specific UI endpoints
- Advanced analytics (pathways, IRs, estimation, prediction)
- Admin/security endpoints
- Data characterization reports

## Naming Convention

This client tries to implement a **predictable naming pattern** that mirrors WebAPI REST endpoints exactly:

- Base endpoints: 
    - `/info` → `client.info()`
    - `/conceptset/` → `client.conceptset()`
    - `/cohortdefinition/` → `client.cohortdefinition()`

- Resource by ID: 
    - `/conceptset/{id}` → `client.conceptset(id)`
    - `/cohortdefinition/{id}` → `client.cohortdefinition(id)`
    - `/job/{id}` → `client.job(id)`

- Sub-resources: 
    - `/conceptset/{id}/expression` → `client.conceptset_expression(id)`
    - `/source/sources` → `client.source.sources()`
    - `/cohortdefinition/{id}/generate/{source}` → `client.cohortdefinition_generate(id, source)`

This attempts to makes the Python code self-documenting. Eg. if you see `client.conceptset()`, you can guess that it calls `GET /conceptset/` in the OHDSI WebAPI. 

The [client code](../src/ohdsi_webapi/client.py) is actually implemented with '[Services](../src/ohdsi_webapi/services/)' - the preditable methods often being shortcuts.  Sometimes it has not been able to create predictable methods aligning to a WebAPI endpoint - in which case the original Service methods can be used.  

----------

### Info & Health

| WebAPI Endpoint | Client method |  Description |
|----------------|---------------|-------------|
| `GET /info` | `client.info()` | WebAPI version and build info |

------------

### Data Sources

| WebAPI Endpoint | Client method |  Description |
|----------------|---------------|-------------|
| `GET /source/sources` | `client.source.sources()` | List all configured data sources |

### 📖 Vocabulary & Concepts

| WebAPI Endpoint | Client method |  Description |
|----------------|---------------|-------------|
| `GET /vocabulary/domains` | `client.vocabulary.domains()` | List all OMOP domains |
| `GET /vocabulary/vocabularies` | `client.vocabulary.vocabularies()` | List all vocabularies |
| `GET /vocabulary/concept/{id}` | `client.vocabulary.concept(id)` | Get single concept by ID |
| `GET /vocabulary/concept/{id}/descendants` | `client.vocabulary.concept_descendants(id)` | Get child concepts |
| `GET /vocabulary/concept/{id}/related` | `client.vocabulary.concept_related(id)` | Get related concepts |
| `POST /vocabulary/search/` | `client.vocabulary.search(query, ...)` | Search concepts by text |
| `POST /vocabulary/concepts` | `client.vocabulary.concepts(ids)` | Bulk retrieve concepts |
| `POST /vocabulary/lookup/identifiers` | `client.vocabulary.lookup_identifiers(...) *` | Map source codes to concepts |

### Concept Sets

| WebAPI Endpoint | Client method |  Description |
|----------------|---------------|-------------|
| `GET /conceptset/` | `client.conceptset()` | List all concept sets |
| `GET /conceptset/{id}` | `client.conceptset(id)` | Get concept set by ID |
| `POST /conceptset/` | `client.conceptset_create(name, expression)` * | Create new concept set |
| `PUT /conceptset/{id}` | `client.conceptset_update(id, concept_set)` * | Update concept set |
| `DELETE /conceptset/{id}` | `client.conceptset_delete(id)` * | Delete concept set |
| `GET /conceptset/{id}/expression` | `client.conceptset_expression(id)` | Get concept set expression |
| `POST /conceptset/{id}/expression` | `client.conceptset_expression.set(id, expr)` | Update expression only |
| `GET /conceptset/{id}/items` | `client.conceptset_items(id)` | Resolve to concrete concepts |
| `GET /conceptset/{id}/export` | `client.conceptset_export(id, format)` | Export as CSV/JSON |
| `GET /conceptset/{id}/generationinfo` | `client.conceptset_generationinfo(id)` | Get generation metadata |

### Cohort Definitions

| WebAPI Endpoint | 'Predictable' method | Service method | Description |
|----------------|---------------|-------------|-----------|
| `GET /cohortdefinition/` | `client.cohortdefinition()` | List all cohort definitions |
| `GET /cohortdefinition/{id}` | `client.cohortdefinition(id)` | Get cohort definition by ID |
| `POST /cohortdefinition/` | `client.cohortdefinition_create(cohort_def)` | Create new cohort definition |
| `PUT /cohortdefinition/{id}` | `client.cohortdefinition_update(id, cohort_def)` | Update cohort definition |
| `DELETE /cohortdefinition/{id}` | `client.cohortdefinition_delete(id)` | Delete cohort definition |
| `POST /cohortdefinition/{id}/generate/{source}` | `client.cohortdefinition_generate(id, source_key)` | Generate cohort on data source |
| `GET /cohortdefinition/{id}/info` | `client.cohortdefinition_info(id)` | Check generation status |
| `GET /cohortdefinition/{id}/inclusionrules/{source}` | `client.cohortdefinition_inclusionrules(id, source)` | Get inclusion rule statistics |

### Job Management

| WebAPI Endpoint | 'Predictable' method | Service method | Description |
|----------------|---------------|-------------|-----------|
| `GET /job/{execution_id}` | `client.job(execution_id)` | Get job execution status |


----------------


## Missing Endpoints

If you need an endpoint that's not listed here, please [open an issue](https://github.com/your-org/ohdsi-webapi-client/issues) or better yet, submit a PR, with:
- The specific WebAPI endpoint you need
- Your use case / why you need it
- Priority (blocking vs. nice-to-have)

