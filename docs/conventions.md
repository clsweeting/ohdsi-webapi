# OHDSI WebAPI Client - Naming Conventions

This document establishes consistent patterns for service method naming across the library.

## Core Principles

1. **Dual Naming Support**: Provide both descriptive and endpoint-style methods
2. **Clarity First**: Descriptive names should clearly indicate the action
3. **WebAPI Alignment**: Endpoint-style aliases should mirror the actual WebAPI paths
4. **Consistency**: Apply patterns uniformly across all services

## Established Patterns

### Single Resource Retrieval
```python
# Primary descriptive method
def get_concept(self, concept_id: int) -> Concept:
    """Fetch a single concept by ID."""

# Endpoint-style alias
def concept(self, concept_id: int) -> Concept:
    """Alias for get_concept() to match WebAPI endpoint path (/vocabulary/concept/{id})."""
    return self.get_concept(concept_id)
```

**WebAPI Path**: `/vocabulary/concept/{id}` → **Methods**: `get_concept(id)` + `concept(id)`

### Collection/List Endpoints
```python
# Primary descriptive method
def list_domains(self) -> list[dict[str, Any]]:
    """Return available vocabulary domains."""

# Endpoint-style alias
def domains(self) -> list[dict[str, Any]]:
    """Alias for list_domains() to match WebAPI endpoint naming (/vocabulary/domains)."""
    return self.list_domains()
```

**WebAPI Path**: `/vocabulary/domains` → **Methods**: `list_domains()` + `domains()`

### CRUD Operations
```python
# Standard CRUD methods (descriptive)
def list(self) -> list[ConceptSet]:           # GET /conceptset/
def get(self, id: int) -> ConceptSet:         # GET /conceptset/{id}
def create(self, name: str) -> ConceptSet:    # POST /conceptset/
def update(self, obj: ConceptSet) -> ConceptSet:  # PUT /conceptset/{id}
def delete(self, id: int) -> None:            # DELETE /conceptset/{id}
```

### Complex Operations
```python
# Descriptive names for multi-step operations
def resolve(self, concept_set_id: int) -> list[ResolvedConceptSetItem]:
def generate(self, cohort_id: int, source_key: str) -> JobStatus:
def poll_generation(self, job: JobStatus, timeout: int = 300) -> JobStatus:
```

## Implementation Standards

### 1. Always Primary + Alias Pattern
- Implement the descriptive method first (contains actual logic)
- Add endpoint-style alias that calls the primary method
- Document the alias relationship clearly

### 2. Method Naming Rules

**Descriptive Methods**:
- Use clear action verbs: `get_`, `list_`, `create_`, `update_`, `delete_`
- Include the resource type for clarity: `get_concept`, `list_domains`
- Use `_many` suffix for bulk operations: `resolve_many`

**Endpoint-Style Aliases**:
- Mirror the WebAPI path structure exactly
- Remove HTTP method prefixes: `/concept/{id}` → `concept(id)`
- For collections, use plural nouns: `/domains` → `domains()`

### 3. Documentation Standards
```python
def get_concept(self, concept_id: int) -> Concept:
    """Fetch a single concept by ID.
    
    Args:
        concept_id: The OMOP concept ID to retrieve
        
    Returns:
        Concept object with all standard OMOP fields
        
    Raises:
        WebApiError: If concept not found or network error
    """

def concept(self, concept_id: int) -> Concept:
    """Alias for get_concept() to match WebAPI endpoint path (/vocabulary/concept/{id})."""
    return self.get_concept(concept_id)
```

## Current Implementation Status

### ✅ VocabularyService
- `get_concept(id)` + `concept(id)` 
- `list_domains()` + `domains()`
- `search()`, `descendants()`, `ancestors()`, `bulk_get()`, `lookup_identifiers()`

### ✅ ConceptSetService  
- `list()`, `get(id)`, `create()`, `update()`, `delete()`
- `expression()`, `included_concepts()`, `generation_info()`

### ✅ CohortService
- `get(id)`, `create()`, `update()`, `delete()`
- `generate()`, `poll_generation()`, `inclusion_rule_stats()`, `generation_count()`

### ✅ SourcesService
- `list()`, `iter()`

## Expansion Guidelines

When adding new endpoints, follow this checklist:

1. **Identify the WebAPI path**: `/vocabulary/concept/{id}/related`
2. **Create descriptive method**: `get_related_concepts(concept_id: int)`
3. **Add endpoint alias**: `related(concept_id: int)` 
4. **Document both**: Primary method gets full docs, alias gets one-liner
5. **Update this document**: Add to implementation status

## Service Aliases at Client Level

The client also supports service aliases for WebAPI endpoint alignment:

```python
# Both styles supported
client.vocabulary.concept(201826)  # endpoint-style
client.vocab.get_concept(201826)   # descriptive

client.conceptset.list()           # endpoint-style  
client.concept_sets.list()         # descriptive
```

This dual-level approach (service aliases + method aliases) provides maximum flexibility for different developer preferences and use cases.
