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

This client uses **predictable REST-style methods** that mirror the WebAPI endpoints directly. It also integrates with the `ohdsi-cohort-schemas` library for type-safe model handling.

```python
from ohdsi_webapi import WebApiClient
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# List concept sets (metadata only) - WARNING: can be 20,000+ items
concept_sets = client.concept_sets.list()
print(len(concept_sets))

# Get a specific concept set by ID
cs = client.concept_sets.get(concept_sets[0].id)
print(cs.name)

# Fetch stored expression (returns structured model)
expr = client.concept_sets.get_expression(cs.id)
print(f"Expression has {len(expr.items)} items")

# Resolve to concrete included concepts 
resolved = client.concept_sets.get_items(cs.id)
print("Resolved count:", len(resolved))
```

## Working with Large Concept Set Lists

The WebAPI `/conceptset/` endpoint returns ALL concept sets without pagination (often 20,000+ on busy servers). To work with large lists efficiently:

```python
# Get all concept sets
all_concept_sets = client.concept_sets.list()

# For basic name filtering, you can filter the list in Python
covid_sets = [cs for cs in all_concept_sets if "covid" in cs.name.lower()][:10]
diabetes_sets = [cs for cs in all_concept_sets if "diabetes" in cs.name.lower()][:5]

# Process concept sets one at a time to avoid memory issues
large_concept_sets = []
for cs in all_concept_sets:
    # Get full details for interesting ones
    if "diabetes" in cs.name.lower():
        expr = client.concept_sets.get_expression(cs.id)
        if len(expr.items) > 10:
            large_concept_sets.append(cs)
    
    # Break early if you find what you need
    if len(large_concept_sets) >= 10:
        break
```

## Creating a New Concept Set

```python
from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

# Build expression using structured models (recommended)
metformin_concept = Concept(
    concept_id=201826,
    concept_name="Metformin",
    standard_concept="S",
    vocabulary_id="RxNorm",
    domain_id="Drug"
)

metformin_item = ConceptSetItem(
    concept=metformin_concept,
    include_descendants=True,
    include_mapped=True,
    is_excluded=False
)

expr = ConceptSetExpression(items=[metformin_item])

# Create the concept set
cs_new = client.concept_sets.create("Metformin Only", expression=expr)
print(cs_new.id)

# Alternative: Build expression as dict (also supported)
metformin_dict = client.vocabulary.get(201826)  # Get concept details
expr_dict = {
    "items": [
        {
            "concept": {
                "CONCEPT_ID": metformin_dict.concept_id,
                "CONCEPT_NAME": metformin_dict.concept_name,
                "STANDARD_CONCEPT": metformin_dict.standard_concept,
                "VOCABULARY_ID": metformin_dict.vocabulary_id,
            },
            "includeDescendants": True,
            "includeMapped": True,
            "isExcluded": False
        }
    ]
}

cs_new = client.concept_sets.create("Metformin Only", expression=expr_dict)
```

## Updating Expression

```python
# Update full ConceptSet object 
cs_new.expression = expr
cs_new = client.concept_sets.update(cs_new.id, cs_new)

# Or update just the expression 
client.concept_sets.set_expression(cs_new.id, expr)
```

## Other Operations

### Exporting a Concept Set  
```python
# Export as CSV or JSON
csv_text = client.concept_sets.export(cs.id, format="csv")
print(csv_text.splitlines()[:5])
```

### Comparing Two Concept Sets
```python
# Compare overlap between concept sets
overlap = client.concept_sets.compare(concept_sets[0].id, concept_sets[1].id)
print(len(overlap))  # structure depends on server version
```

### Generation Info
```python
# Get metadata about where the concept set has been used
gen_info = client.concept_sets.get_generation_info(cs.id)
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
    cs = client.concept_sets.get(999999)
except WebApiError as e:
    print("Not found", e.status_code)
```

## Roadmap Enhancements (Future)
- Helper builder API for easier expression construction (add_concept, exclude_concept, etc.)
- Diff utility returning added/removed concept IDs  
- Validation of expression structure before submission
- Better filtering and search capabilities for large concept set lists
