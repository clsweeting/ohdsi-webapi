# Vocabulary & Concepts

This guide shows how to use the `VocabularyService` via `client.vocab` to interact with OHDSI / OMOP vocabulary data when you may not be deeply familiar with OMOP conventions.

## OMOP Vocabulary Basics (Quick Primer)
- Each medical concept (drug, condition, procedure, etc.) has a unique numeric `conceptId`.
- Concepts have attributes: `conceptName`, `domainId` (broad category e.g. Drug), `vocabularyId` (source of terminology e.g. RxNorm, SNOMED), `conceptClassId` (refined classification), and may have a `standardConcept` flag (`'S'` = standard, `'C'` = classification, blank = non-standard).
- Hierarchies: Concepts can have ancestor/descendant relationships (e.g., Ingredient → Clinical Drug Form → Clinical Drug).
- Mapping: Non-standard source codes map to standard concepts. Use these mappings for consistent analytics.

## Setup
```python
from ohdsi_webapi import WebApiClient
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
```

## Get a Concept by ID
```python
concept = client.vocab.get_concept(201826)  # Metformin
print(concept.concept_name, concept.domainId, concept.vocabularyId)
```

## Text Search
Search across vocabularies for matching text.
```python
results = client.vocab.search("metformin", standard_concept="S", domain_id="Drug", page_size=50)
for c in results:
    print(c.concept_id, c.concept_name, c.standardConcept)
```
Parameters:
- `standard_concept`: filter to standard concepts (`"S"`).
- `domain_id`: restrict to a domain (e.g., "Drug", "Condition").
- `concept_class_id`: narrow to a specific concept class.
- `vocabulary_id`: restrict to a vocabulary (e.g., "RxNorm").

## Bulk Fetch Concepts
When you have concept IDs already, batch fetch saves round trips.
```python
concepts = client.vocab.bulk_get([201826, 1503297])
```

## Hierarchies: Ancestors & Descendants
```python
children = client.vocab.descendants(201826)
parents = client.vocab.ancestors(201826)
```
Typical use: expand an ingredient to all clinical drug forms & branded variants via descendants.

## Domains List
List available domains (e.g., Drug, Condition, Measurement).
```python
domains = client.vocab.list_domains()
print([d['domainId'] for d in domains])
```

## Code → Concept Lookup (Identifiers)
Use when you have source codes (e.g., NDC, ICD10CM) and need OMOP concepts.
```python
lookup = client.vocab.lookup_identifiers([
    ("50096", "RxNorm"),  # Example code
    {"identifier": "A10BA02", "vocabularyId": "ATC", "includeMapped": True},
])
for c in lookup:
    print(c.concept_id, c.concept_name)
```
Flags:
- `include_mapped`: include mapped standard concepts for non-standard codes.
- `include_descendants`: include descendant concepts (hierarchical expansion) where relevant.

## Choosing Standard vs Non-Standard Concepts
- Analytics (cohorts, feature extraction) should use standard concepts (`standardConcept == 'S'`).
- Source codes without a standard flag require mapping to the standard concept (the API often provides mapping endpoints; lookups with `includeMapped=True` help).

## Validity Dates
Concepts have `validStartDate` / `validEndDate`. If current date > `validEndDate` and `invalidReason` is not null, the concept is deprecated; find replacements via mapping tables (future enhancement: add helper).

## Performance Tips
- Batch IDs via `bulk_get` instead of looping `get_concept`.
- Use search filters to reduce payload size.
- Cache stable concept metadata in your application layer if you call often.

## Error Handling
All HTTP / parsing issues raise `WebApiError` subclasses. Wrap calls if you need custom fallback logic:
```python
from ohdsi_webapi.exceptions import WebApiError
try:
    c = client.vocab.get_concept(999999999)
except WebApiError as e:
    print("Lookup failed", e.status_code, e.endpoint)
```

## Next Steps
See upcoming guides for concept sets and cohorts. Open issues or feature requests are welcome.
