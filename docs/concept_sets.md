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


## Concept Sets vs. Concept Set Items vs. Expressions 

Understanding the distinction between these three concepts is crucial for working with OHDSI concept sets:

### ConceptSet
- **Purpose**: a complete, reusable group of medical concepts with metadata
- **Structure**: contains an ID, name, and expression
- **Usage**: This is what gets stored and managed in the OHDSI WebAPI
- **Components**:
  - `id`: Unique identifier within the cohort definition
  - `name`: Human-readable name (e.g., "Type 2 Diabetes Mellitus")
  - `expression`: The logic defining which concepts are included

### ConceptSetExpression
- **Purpose**: Defines the logical rules for which concepts should be included in the set
- **Structure**: Contains a list of ConceptSetItems
- **Usage**: This is the "recipe" or "formula" that defines the concept set
- **Components**:
  - `items`: A list of ConceptSetItem objects that define the inclusion/exclusion rules

### ConceptSetItem
- **Purpose**: Represents a single concept and its inclusion/exclusion rules within a concept set
- **Structure**: Contains one OMOP concept plus behavioral flags
- **Usage**: This is a single "ingredient" in the concept set recipe
- **Components**:
  - `concept`: An OMOP Concept (with ID, name, vocabulary, etc.)
  - `include_descendants`: Whether to include child concepts in the hierarchy
  - `include_mapped`: Whether to include concepts mapped from source vocabularies
  - `is_excluded`: Whether this concept should be subtracted from the set

### Hierarchy and Relationship

```
ConceptSet
├── id: 0
├── name: "Type 2 Diabetes Mellitus"
└── expression: ConceptSetExpression
    └── items: [ConceptSetItem, ConceptSetItem, ...]
        ├── ConceptSetItem
        │   ├── concept: Concept (ID: 201826, "Type 2 diabetes mellitus")
        │   ├── include_descendants: true
        │   ├── include_mapped: false
        │   └── is_excluded: false
        └── ConceptSetItem
            ├── concept: Concept (ID: 201254, "Type 1 diabetes mellitus") 
            ├── include_descendants: true
            ├── include_mapped: false
            └── is_excluded: true  # Exclude Type 1 from Type 2 set
```

### Key Distinction

- **ConceptSet** = The complete package (metadata + logic)
- **ConceptSetExpression** = The logic/rules only
- **ConceptSetItem** = Individual concept + its inclusion/exclusion behavior

The Expression is the "brain" of the ConceptSet - it defines which concepts get included or excluded and how hierarchical relationships are handled. When the WebAPI "resolves" a concept set, it takes the Expression and expands it into a concrete list of concept IDs based on the vocabulary hierarchy and mapping rules.

### Structure of an Expression (Simplified)
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
concept_sets = client.conceptset()    # Since the WebAPI method is GET /conceptset 
print(len(concept_sets))

# Get a specific concept set by ID
cs = client.conceptset(concept_sets[0].id)
print(cs.name)

# Fetch stored expression (returns structured model)
expr = client.conceptset_expression(cs.id)
print(expr)

# Resolve to concrete included concepts 
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

```

## Creating a New Concept Set

```python
from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept
from datetime import datetime

# Build expression using structured models (recommended)
metformin_concept = Concept(
    concept_id=98061,
    concept_name="Metformin",
    concept_code="98061",  
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

# Create unique name with timestamp to avoid 409 conflicts
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
concept_set_name = f"Metformin Only - {timestamp}"

# Create the concept set - convert model to dict
cs_new = client.concept_sets.create(concept_set_name, expression=expr.model_dump(by_alias=True))
print(cs_new.id)

# Alternative: Build expression as dict (also supported)
metformin_dict = client.vocabulary.concept(201826)  # Get concept details
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

# Use same timestamp approach for alternative method
alternative_name = f"Metformin Only (Dict) - {timestamp}"
cs_new = client.concept_sets.create(alternative_name, expression=expr_dict)
```

> [!CAUTION]
> **JSON Serialization Error Fix:** If you get `TypeError: Object of type ConceptSetExpression is not JSON serializable`, you need to convert Pydantic models to dictionaries before sending to the API:
> 
> ```python
> # ❌ Wrong - passing Pydantic model directly
> cs_new = client.conceptset_create("Name", expression=expr)
> 
> # ✅ Correct - convert to dict with proper aliases
> cs_new = client.conceptset_create("Name", expression=expr.model_dump(by_alias=True))
> ```
> 
> The `by_alias=True` parameter ensures field names match the WebAPI format (e.g., `includeDescendants` instead of `include_descendants`).

## Updating Expression

```python
# Update full ConceptSet object 
cs_new.expression = expr
cs_new = client.conceptset_update(cs_new)

# Or update just the expression 
client.conceptset_expression(cs_new.id, expr)
```

## Other Operations

### Exporting a Concept Set  
```python
# Export as CSV or JSON
csv_text = client.conceptset_export(cs.id, format="csv")
print(csv_text.splitlines()[:5])
```

### Generation Info
```python
# Get metadata about where the concept set has been used
gen_info = client.conceptset_generationinfo(cs.id)
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
    cs = client.conceptset(999999)
except WebApiError as e:
    print("Not found", e.status_code)
```

## Roadmap Enhancements (Future)
- Helper builder API for easier expression construction (add_concept, exclude_concept, etc.)
- Diff utility returning added/removed concept IDs  
- Validation of expression structure before submission
- Better filtering and search capabilities for large concept set lists
