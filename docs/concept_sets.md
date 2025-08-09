# Concept Sets

Concept sets define groups of concepts (e.g., drugs for diabetes) using a structured expression that can include/exclude concepts and descendants/mapped concepts. They are reusable in cohort definitions and analyses.

## Key Ideas
- A Concept Set stores a concise expression (seed concepts + flags) rather than an enumerated list.
- Resolving a concept set expands the expression into concrete included concepts (applying descendants/mapped logic).
- You can fetch, update, and reuse concept sets across analyses.

## Structure of an Expression (Simplified)
```json
{
  "items": [
    {
      "concept": {
        "CONCEPT_ID": 201826,
        "CONCEPT_NAME": "Metformin",
        "STANDARD_CONCEPT": "S",
        "VOCABULARY_ID": "RxNorm"
      },
      "isExcluded": false,
      "includeDescendants": true,
      "includeMapped": true
    }
  ]
}
```
Flags:
- `includeDescendants`: include all hierarchical descendants of the seed concept (e.g., all specific dose forms of an ingredient).
- `includeMapped`: include concepts mapped (e.g., source vocab to standard) when relevant.
- `isExcluded`: subtract this branch from the cumulative set.

## Basic Operations
```python
from ohdsi_webapi import WebApiClient
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# List concept sets (metadata only) - WARNING: can be 20,000+ items
concept_sets = client.concept_sets.list()
print(len(concept_sets))

# RECOMMENDED: Use filtering for large lists
covid_sets = client.concept_sets.list_filtered(name_contains="covid", limit=10)
diabetes_sets = client.concept_sets.list_filtered(name_contains="diabetes", limit=5)

# Memory-efficient processing of all concept sets
for concept_set in client.concept_sets.iter_all():
    if len(concept_set.expression.get('items', [])) > 50:
        print(f"Large concept set: {concept_set.name}")
    # Break early if you don't need to process all 20k+ items
    break

# Pick one and fetch full details
cs = client.concept_sets.get(concept_sets[0].id)
print(cs.name)

# Fetch stored expression
expr = client.concept_sets.expression(cs.id)
print(expr.get("items", []))

# Resolve to concrete included concepts
resolved = client.concept_sets.resolve(cs.id)
print("Resolved count:", len(resolved))
```

## Working with Large Concept Set Lists

The WebAPI `/conceptset/` endpoint returns ALL concept sets without pagination (often 20,000+ on busy servers). Use these methods for practical access:

### Filtered Search
```python
# Find concept sets by name
covid_sets = client.concept_sets.list_filtered(name_contains="covid", limit=10)
drug_sets = client.concept_sets.list_filtered(name_contains="drug", limit=20)

# Filter by tags (if your server uses tagging)
tagged_sets = client.concept_sets.list_filtered(tags=["validated", "research"])

# Combine filters
research_diabetes = client.concept_sets.list_filtered(
    name_contains="diabetes", 
    tags=["research"], 
    limit=5
)
```

### Memory-Efficient Processing
```python
# Process all concept sets without loading everything into memory
large_concept_sets = []
for cs in client.concept_sets.iter_all():
    if cs.expression and len(cs.expression.get('items', [])) > 100:
        large_concept_sets.append(cs)
    
    # Break early if you find what you need
    if len(large_concept_sets) >= 10:
        break
```

## Creating a New Concept Set
```python
# Build expression programmatically
metformin = client.vocab.get_concept(201826)
expr = {
    "items": [
        {
            "concept": {
                "CONCEPT_ID": metformin.conceptId,
                "CONCEPT_NAME": metformin.conceptName,
                "STANDARD_CONCEPT": metformin.standardConcept,
                "VOCABULARY_ID": metformin.vocabularyId,
            },
            "includeDescendants": True,
            "includeMapped": True,
            "isExcluded": False
        }
    ]
}
cs_new = client.concept_sets.create("Metformin Only", expression=expr)
print(cs_new.id)
```

## Updating Expression (Partial vs Full)
Two approaches:
1. Update full ConceptSet object (we already hold its id & expression):
```python
cs_new.expression = expr
cs_new = client.concept_sets.update(cs_new)
```
2. Replace just the expression (does not change other metadata):
```python
client.concept_sets.set_expression(cs_new.id, expr)
```

## Bulk Resolve Multiple Concept Sets
If supported by the server:
```python
mapping = client.concept_sets.resolve_many([cs.id for cs in concept_sets[:3]])
for cid, items in mapping.items():
    print(cid, len(items))
```
Falls back to sequential resolution if bulk endpoint unsupported.

## Exporting a Concept Set
```python
csv_text = client.concept_sets.export(cs.id, format="csv")
print(csv_text.splitlines()[:5])
```

## Comparing Two Concept Sets
```python
overlap = client.concept_sets.compare(concept_sets[0].id, concept_sets[1].id)
print(len(overlap))  # structure depends on server version
```

## Included Concepts Shortcut
Some servers expose an endpoint returning included concept rows without fully resolving:
```python
included = client.concept_sets.included_concepts(cs.id)
print(len(included))
```
If endpoint not available, this returns an empty list.

## Generation Info
Optional metadata about where the concept set has been used:
```python
gen_info = client.concept_sets.generation_info(cs.id)
print(gen_info)
```
May be empty or unsupported.

## Best Practices
- Keep concept sets focused: separate drug exposure and condition concept sets rather than mixing domains.
- Use standard concepts whenever possible; rely on `includeMapped` only when necessary.
- Version control important concept sets by exporting expression JSON.

## Error Handling
Methods raise `WebApiError` subclasses on HTTP issues. Wrap calls if you need fallbacks:
```python
from ohdsi_webapi.exceptions import WebApiError
try:
    client.concept_sets.get(999999)
except WebApiError as e:
    print("Not found", e.status_code)
```

## Roadmap Enhancements (Future)
- Helper builder API (add_concept, exclude_concept, etc.)
- Diff utility returning added/removed concept IDs
- Validation of expression structure
