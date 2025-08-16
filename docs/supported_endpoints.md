# Supported WebAPI Endpoints

This page lists all OHDSI WebAPI endpoints currently supported by this Python client. The [official WebAPI documentation](http://webapidoc.ohdsi.org/index.html) shows hundreds of endpoints, but this client focuses on the core functionality needed for cohort building and vocabulary operations.

## Coverage Philosophy

This client prioritizes **cohort building workflows** and covers these key areas:
- ✅ **Vocabulary & Concepts** - Search and retrieve medical concepts
- ✅ **Concept Sets** - Create and manage reusable concept groups  
- ✅ **Cohort Definitions** - Define and generate patient cohorts
- ✅ **Sources** - List available data sources
- ✅ **Info & Health** - WebAPI version and status information

**Not Currently Supported:**
- Atlas-specific UI endpoints
- Advanced analytics (pathways, IRs, estimation, prediction)
- Admin/security endpoints
- Data characterization reports

## Naming Convention

This client follows a **predictable naming pattern** that mirrors WebAPI REST endpoints exactly:

- **Base endpoints**: `/info` → `client.info()`, `/conceptset/` → `client.conceptset()`, `/cohortdefinition/` → `client.cohortdefinition()`
- **Resource by ID**: `/conceptset/{id}` → `client.conceptset(id)`, `/cohortdefinition/{id}` → `client.cohortdefinition(id)`, `/job/{id}` → `client.job(id)`
- **Sub-resources**: `/conceptset/{id}/expression` → `client.conceptset_expression(id)`, `/source/sources` → `client.sources.list()`
- **Actions**: `/cohortdefinition/{id}/generate/{source}` → `client.cohortdefinition_generate(id, source)`

This makes the Python code self-documenting - if you see `client.conceptset()`, you immediately know it calls `GET /conceptset/`.

### 🏥 Info & Health

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /info` | `client.info()` | WebAPI version and build info |

### 📊 Data Sources

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /source/sources` | `client.sources.list()` | List all configured data sources |

### 📖 Vocabulary & Concepts

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /vocabulary/domains` | `client.vocabulary.domains()` | List all OMOP domains |
| `GET /vocabulary/vocabularies` | `client.vocabulary.vocabularies()` | List all vocabularies |
| `GET /vocabulary/concept/{id}` | `client.vocabulary.concept(id)` | Get single concept by ID |
| `GET /vocabulary/concept/{id}/descendants` | `client.vocabulary.concept_descendants(id)` | Get child concepts |
| `GET /vocabulary/concept/{id}/related` | `client.vocabulary.concept_related(id)` | Get related concepts |
| `POST /vocabulary/search/` | `client.vocabulary.search(query, ...)` | Search concepts by text |
| `POST /vocabulary/concepts` | `client.vocabulary.concepts(ids)` | Bulk retrieve concepts |
| `POST /vocabulary/lookup/identifiers` | `client.vocabulary.lookup_identifiers(...)` | Map source codes to concepts |

### 📋 Concept Sets

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /conceptset/` | `client.conceptset()` | List all concept sets |
| `GET /conceptset/{id}` | `client.conceptset(id)` | Get concept set by ID |
| `POST /conceptset/` | `client.conceptset.create(name, expression)` | Create new concept set |
| `PUT /conceptset/{id}` | `client.conceptset.update(id, concept_set)` | Update concept set |
| `DELETE /conceptset/{id}` | `client.conceptset.delete(id)` | Delete concept set |
| `GET /conceptset/{id}/expression` | `client.conceptset_expression(id)` | Get concept set expression |
| `POST /conceptset/{id}/expression` | `client.conceptset_expression.set(id, expr)` | Update expression only |
| `GET /conceptset/{id}/items` | `client.conceptset_items(id)` | Resolve to concrete concepts |
| `GET /conceptset/{id}/export` | `client.conceptset_export(id, format)` | Export as CSV/JSON |
| `POST /conceptset/compare` | `client.conceptset.compare(id1, id2)` | Compare two concept sets |
| `GET /conceptset/{id}/generationinfo` | `client.conceptset_generationinfo(id)` | Get generation metadata |

### 👥 Cohort Definitions

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /cohortdefinition/` | `client.cohortdefinition()` | List all cohort definitions |
| `GET /cohortdefinition/{id}` | `client.cohortdefinition(id)` | Get cohort definition by ID |
| `POST /cohortdefinition/` | `client.cohortdefinition.create(cohort_def)` | Create new cohort definition |
| `PUT /cohortdefinition/{id}` | `client.cohortdefinition.update(id, cohort_def)` | Update cohort definition |
| `DELETE /cohortdefinition/{id}` | `client.cohortdefinition.delete(id)` | Delete cohort definition |
| `POST /cohortdefinition/{id}/generate/{source}` | `client.cohortdefinition_generate(id, source_key)` | Generate cohort on data source |
| `GET /cohortdefinition/{id}/info` | `client.cohortdefinition_info(id)` | Check generation status |
| `GET /cohortdefinition/{id}/inclusionrules/{source}` | `client.cohortdefinition_inclusionrules(id, source)` | Get inclusion rule statistics |

### ⚙️ Job Management

| WebAPI Endpoint | Python Method | Description |
|----------------|---------------|-------------|
| `GET /job/{execution_id}` | `client.job(execution_id)` | Get job execution status |

## Usage Examples

### Basic Workflow: Building a Diabetes Cohort

```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://your-webapi-url.com")

# 1. Search for diabetes concepts
diabetes_concepts = client.vocabulary.search("type 2 diabetes", domain_id="Condition")
main_concept = diabetes_concepts[0]

# 2. Create a concept set
concept_set_expr = {
    "items": [{
        "concept": {"conceptId": main_concept.concept_id},
        "includeDescendants": True,
        "isExcluded": False
    }]
}
diabetes_cs = client.conceptset.create("Type 2 Diabetes", concept_set_expr)

# 3. Create cohort definition (simplified)
cohort_expr = {
    "PrimaryCriteria": {...},  # Your cohort logic here
    "ConceptSets": [diabetes_cs.expression]
}
cohort = client.cohortdefinition.create({
    "name": "T2DM Patients", 
    "expression": cohort_expr
})

# 4. Generate on a data source
sources = client.sources.list()
source_key = sources[0].source_key
status = client.cohortdefinition_generate(cohort.id, source_key)

# 5. Check generation status
final_status = client.cohortdefinition_info(cohort.id)
```

### Quick Reference

```python
# Health check
info = client.info()

# List available data sources
sources = client.sources.list()

# Search vocabulary
domains = client.vocabulary.domains()
concepts = client.vocabulary.search("diabetes")

# Work with concept sets
concept_sets = client.conceptset()
cs = client.conceptset(123)
expression = client.conceptset_expression(123)

# Work with cohort definitions  
cohorts = client.cohortdefinition()
cohort = client.cohortdefinition(456)
client.cohortdefinition_generate(456, "SYNPUF")

# Check job status
status = client.job("execution-uuid")
```
print(f"Generation {final_status.status}")
```

### Using Both Predictable and Shortcut Methods

```python
# These are equivalent - use whichever feels more natural:

# Predictable (matches REST endpoints exactly)
concept_sets = client.conceptset()  # GET /conceptset/
diabetes_cs = client.conceptset(123)  # GET /conceptset/123
expression = client.conceptset_expression(123)  # GET /conceptset/123/expression

cohorts = client.cohortdefinition()  # GET /cohortdefinition/
my_cohort = client.cohortdefinition(456)  # GET /cohortdefinition/456

# Shortcuts (pythonic, backwards compatible)
concept_sets = client.concept_sets.list()
diabetes_cs = client.concept_sets.get(123)
expression = client.concept_sets.expression(123)

cohorts = client.cohorts.list()
my_cohort = client.cohorts.get(456)
```

## Missing Endpoints

If you need an endpoint that's not listed here, please [open an issue](https://github.com/your-org/ohdsi-webapi-client/issues) with:
- The specific WebAPI endpoint you need
- Your use case / why you need it
- Priority (blocking vs. nice-to-have)

We prioritize endpoints based on cohort building workflows, but we're open to expanding coverage based on community needs.

## Endpoint Discovery

To explore what's available in your WebAPI instance:

```python
# Check WebAPI version and capabilities
info = client.info.get()
print(f"WebAPI Version: {info.version}")

# List available data sources
sources = client.sources.list()
for source in sources:
    print(f"Source: {source.source_name} ({source.source_key})")

# List domains and vocabularies
domains = client.vocabulary.domains()
vocabularies = client.vocabulary.vocabularies()
print(f"Available: {len(domains)} domains, {len(vocabularies)} vocabularies")
```

This gives you a quick overview of what your specific WebAPI instance supports.
