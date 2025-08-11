# Concept Sets

The OMOP Vocabulary maps many different source vocabularies (ICD-10, Read Codes, MedDRA, etc.) into standard concepts.

When you want to say “patients with Type 2 diabetes” or “prescriptions for statins”, you don’t want to hand-pick ICD-10 or SNOMED codes each time.   Concept Sets let you bundle all those relevant concepts into a single reusable set, so your definition is consistent, transparent & portable. 

Concept Sets in OHDSI are only about clinical or vocabulary concepts —
so they cover conditions, drugs, procedures, measurements, devices, etc. — but not demographics like age, sex, or visit type.


## OMOP Vocabulary Concepts 

Concept Sets are built from OMOP Vocabulary concepts, which include domains such as:
- Condition — e.g., Type 2 diabetes mellitus, Asthma
- Drug — e.g., Metformin 500 mg oral tablet
- Procedure — e.g., Appendectomy
- Measurement — e.g., HbA1c measurement
- Observation — e.g., Smoking status
- Device — e.g., Pacemaker
- Specimen, Visit, and other clinical domains

They’re essentially lists of standard concepts that you can later reference in [cohort logic](cohorts.md).



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

This client uses **predictable REST-style methods** that mirror the WebAPI endpoints directly. See the [Supported Endpoints](supported_endpoints.md) page for the complete mapping.

```python
from ohdsi_webapi import WebApiClient
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# List concept sets (metadata only) - WARNING: can be 20,000+ items
# GET /conceptset/ -> client.conceptset()
concept_sets = client.conceptset()
print(len(concept_sets))

# Get a specific concept set by ID
# GET /conceptset/{id} -> client.conceptset(id)
cs = client.conceptset(concept_sets[0].id)
print(cs.name)

# Fetch stored expression 
# GET /conceptset/{id}/expression -> client.conceptset_expression(id)
expr = client.conceptset_expression(cs.id)
print(expr.get("items", []))

# Resolve to concrete included concepts 
# GET /conceptset/{id}/items -> client.conceptset_items(id)
resolved = client.conceptset_items(cs.id)
print("Resolved count:", len(resolved))
```

## Working with Large Concept Set Lists

The WebAPI `/conceptset/` endpoint returns ALL concept sets without pagination (often 20,000+ on busy servers). To work with large lists efficiently:

```python
# Get all concept sets
all_concept_sets = client.conceptset()

# For basic name filtering, you can filter the list in Python
covid_sets = [cs for cs in all_concept_sets if "covid" in cs.name.lower()][:10]
diabetes_sets = [cs for cs in all_concept_sets if "diabetes" in cs.name.lower()][:5]

# Process concept sets one at a time to avoid memory issues
large_concept_sets = []
for cs in all_concept_sets:
    # Get full details for interesting ones
    if "diabetes" in cs.name.lower():
        expr = client.conceptset_expression(cs.id)
        if len(expr.get('items', [])) > 10:
            large_concept_sets.append(cs)
    
    # Break early if you find what you need
    if len(large_concept_sets) >= 10:
        break
```

## Creating a New Concept Set

```python
# Build expression programmatically
metformin = client.vocabulary.concept(201826)  # GET /vocabulary/concept/201826
expr = {
    "items": [
        {
            "concept": {
                "CONCEPT_ID": metformin.concept_id,
                "CONCEPT_NAME": metformin.concept_name,
                "STANDARD_CONCEPT": metformin.standardConcept,
                "VOCABULARY_ID": metformin.vocabularyId,
            },
            "includeDescendants": True,
            "includeMapped": True,
            "isExcluded": False
        }
    ]
}

# Create the concept set
# POST /conceptset/ -> client.conceptset.create()
cs_new = client.conceptset.create("Metformin Only", expression=expr)
print(cs_new.id)
```

## Updating Expression

```python
# Update full ConceptSet object 
cs_new.expression = expr
cs_new = client.conceptset.update(cs_new)  # PUT /conceptset/{id}

# Or update just the expression 
client.concept_sets.set_expression(cs_new.id, expr)  # POST /conceptset/{id}/expression
```

## Other Operations

### Exporting a Concept Set  
```python
# Export as CSV or JSON
csv_text = client.conceptset_export(cs.id, format="csv")  # GET /conceptset/{id}/export
print(csv_text.splitlines()[:5])
```

### Comparing Two Concept Sets
```python
# Compare overlap between concept sets
overlap = client.concept_sets.compare(concept_sets[0].id, concept_sets[1].id)  # POST /conceptset/compare
print(len(overlap))  # structure depends on server version
```

### Generation Info
```python
# Get metadata about where the concept set has been used
gen_info = client.conceptset_generationinfo(cs.id)  # GET /conceptset/{id}/generationinfo
print(gen_info)  # May be empty or unsupported
```

## Best Practices
- Keep concept sets focused: separate drug exposure and condition concept sets rather than mixing domains.
- Use standard concepts whenever possible; rely on `includeMapped` only when necessary.
- Version control important concept sets by exporting expression JSON.

## Error Handling

Methods raise `WebApiError` subclasses on HTTP issues. Wrap calls if you need fallbacks:

```python
from ohdsi_webapi.exceptions import WebApiError

try:
    cs = client.conceptset(999999)  # GET /conceptset/999999
except WebApiError as e:
    print("Not found", e.status_code)
```

## Roadmap Enhancements (Future)
- Helper builder API for easier expression construction (add_concept, exclude_concept, etc.)
- Diff utility returning added/removed concept IDs  
- Validation of expression structure before submission
- Better filtering and search capabilities for large concept set lists
