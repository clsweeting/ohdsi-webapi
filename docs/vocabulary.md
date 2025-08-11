# Vocabulary & Concepts in OHDSI

## What is a Medical Vocabulary?

In healthcare data, different organizations use different coding systems to record the same information. For example, "heart attack" might be coded as:
- `410.9` in ICD-9
- `I21.9` in ICD-10  
- `22298006` in SNOMED CT

A **vocabulary** in OHDSI is simply one of these coding systems. The OMOP Common Data Model brings them all together so you can work with medical concepts consistently across different data sources.

### Common Vocabularies in OMOP

| Vocabulary | What It Covers | Example |
|------------|----------------|---------|
| **SNOMED CT** | Clinical findings, conditions, procedures | `201826` = "Type 2 diabetes mellitus" |
| **RxNorm** | Drugs and medications | `1503297` = "Metformin 500 mg tablet" |
| **LOINC** | Lab tests and measurements | `4548-4` = "Hemoglobin A1c" |
| **ICD-10-CM** | Diagnoses (for billing) | `E11.9` = "Type 2 diabetes without complications" |
| **CPT4** | Medical procedures | `99213` = "Office visit, established patient" |

## Understanding Domains vs Vocabularies

This is a key concept that often confuses newcomers:

### 🏷️ Vocabulary = "Where did this code come from?"
**Vocabulary** tells you the source coding system:
- `SNOMED` - from SNOMED CT
- `RxNorm` - from RxNorm  
- `ICD10CM` - from ICD-10-CM

### 📁 Domain = "What type of medical concept is this?"
**Domain** tells you the category for analysis purposes:
- `Condition` - diseases, symptoms, clinical findings
- `Drug` - medications and drug products
- `Procedure` - medical interventions
- `Measurement` - lab tests, vital signs
- `Observation` - other clinical observations

### Example: Same Concept, Different Perspectives

```
Concept ID: 201826
Concept Name: "Type 2 diabetes mellitus"
Vocabulary: SNOMED    ← "This code comes from SNOMED CT"
Domain: Condition     ← "This belongs in the Condition table for analysis"
```

**Why this matters**: When building cohorts, you search by **domain** ("show me all conditions") but the results might come from multiple **vocabularies** (SNOMED, ICD-10, etc.).

## OMOP Database Structure

The vocabulary data lives in these key tables:

| Table | What It Contains |
|-------|------------------|
| `VOCABULARY` | List of all coding systems (SNOMED, RxNorm, etc.) |
| `CONCEPT` | All medical concepts from all vocabularies |
| `CONCEPT_RELATIONSHIP` | How concepts relate to each other |
| `CONCEPT_ANCESTOR` | Parent/child hierarchies (e.g., "diabetes" → "type 2 diabetes") |

## Working with the Vocabulary API

### Setup

```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://your-webapi-url.com")
# The vocabulary service is available as both:
# client.vocabulary (full name) or client.vocab (shorter alias)
```

### 1. Looking Up a Specific Concept

If you know the concept ID:

```python
# Get a specific concept by ID
concept = client.vocab.get_concept(201826)  # Type 2 diabetes

print(f"Name: {concept.concept_name}")
print(f"Domain: {concept.domain_id}")  
print(f"Vocabulary: {concept.vocabulary_id}")
print(f"Standard: {concept.standard_concept}")
```

### 2. Searching for Concepts by Text

This is usually how you start - you know what you're looking for but need the concept ID:

```python
# Search for diabetes-related concepts
results = client.vocab.search(
    query="diabetes",
    domain_id="Condition",        # Only conditions
    standard_concept="S",         # Only standard concepts
    page_size=20
)

for concept in results:
    print(f"{concept.concept_id}: {concept.concept_name}")
```

**Search Parameters:**
- `query` - Text to search for in concept names
- `domain_id` - Filter by domain ("Condition", "Drug", "Procedure", etc.)
- `vocabulary_id` - Filter by vocabulary ("SNOMED", "RxNorm", etc.)
- `concept_class_id` - Filter by concept class ("Clinical Finding", "Ingredient", etc.)
- `standard_concept` - "S" for standard concepts (recommended for analysis)

### 3. Working with Concept Hierarchies

Medical concepts are organized in hierarchies. For example:
- Diabetes (parent)
  - Type 1 diabetes (child)
  - Type 2 diabetes (child)

```python
# Get all child concepts (more specific) - predictable naming
children = client.vocab.concept_descendants(201826)  # All types of diabetes
print(f"Found {len(children)} more specific diabetes concepts")

# Get all related concepts - predictable naming
related = client.vocab.concept_related(201826)  # Related concepts
print(f"Found {len(related)} related concepts")
```

**When to use hierarchies:**
- **Descendants**: When you want to be inclusive (e.g., find all types of diabetes)
- **Related**: When you want to find mapped or associated concepts

### 4. Bulk Operations

When you have multiple concept IDs, batch them for better performance:

```python
concept_ids = [201826, 1503297, 4548-4]  # diabetes, metformin, A1c
concepts = client.vocab.concepts(concept_ids)  # Predictable naming

for concept in concepts:
    print(f"{concept.concept_id}: {concept.concept_name} ({concept.domain_id})")
```

### 5. Converting Source Codes to OMOP Concepts

When you have codes from other systems (like ICD-10 or NDC codes), you need to map them to OMOP concepts:

```python
# Look up codes from other systems
lookup_results = client.vocab.lookup_identifiers([
    {"identifier": "E11.9", "vocabularyId": "ICD10CM"},  # ICD-10 code
    {"identifier": "50096", "vocabularyId": "NDC"},      # NDC drug code
])

for result in lookup_results:
    if result.standard_concept == "S":
        print(f"Standard concept: {result.concept_id} - {result.concept_name}")
```

### 6. Exploring Available Domains and Vocabularies

To see what types of medical data are available:

```python
# List all domains (Condition, Drug, Procedure, etc.)
domains = client.vocab.list_domains()
for domain in domains:
    print(f"{domain['domainId']}: {domain['domainName']}")
```

To see what vocabularies (coding systems) are available:

```python
# List all vocabularies (SNOMED, RxNorm, ICD-10, etc.)
vocabularies = client.vocab.list_vocabularies()
for vocab in vocabularies:
    print(f"{vocab['vocabularyId']}: {vocab['vocabularyName']}")
```

## Standard vs Non-Standard Concepts

This is crucial for analysis:

### ✅ Standard Concepts (`standard_concept = "S"`)
- **Use these for analysis and cohort building**
- Consistent across all OMOP databases
- One "best" concept per medical entity
- Example: SNOMED concept for "Type 2 diabetes"

### ❌ Non-Standard Concepts
- Original source codes (ICD-10, local hospital codes, etc.)  
- **Don't use these for analysis**
- Map to standard concepts instead
- Example: ICD-10 code `E11.9` maps to SNOMED `201826`

```python
# Always filter to standard concepts for analysis
standard_diabetes = client.vocab.search(
    query="diabetes",
    standard_concept="S",  # This is key!
    domain_id="Condition"
)
```

## Practical Examples

### Example 1: Building a Diabetes Cohort

```python
# 1. Search for diabetes concepts
diabetes_concepts = client.vocab.search(
    query="type 2 diabetes",
    domain_id="Condition", 
    standard_concept="S"
)

# 2. Pick the main concept
main_diabetes = diabetes_concepts[0]  # Usually the first result
print(f"Using: {main_diabetes.concept_id} - {main_diabetes.concept_name}")

# 3. Get all related diabetes concepts (more inclusive)
all_diabetes = client.vocab.descendants(main_diabetes.concept_id)
print(f"Including {len(all_diabetes)} related concepts")
```

### Example 2: Finding Medications

```python
# Search for metformin (diabetes medication)
metformin_drugs = client.vocab.search(
    query="metformin",
    domain_id="Drug",
    standard_concept="S"
)

for drug in metformin_drugs[:5]:  # Show first 5
    print(f"{drug.concept_id}: {drug.concept_name}")
    print(f"  Class: {drug.concept_class_id}")
```

### Example 3: Lab Tests and Measurements

```python
# Find A1C lab test (diabetes monitoring)
a1c_tests = client.vocab.search(
    query="hemoglobin a1c",
    domain_id="Measurement",
    standard_concept="S"
)

for test in a1c_tests:
    print(f"{test.concept_id}: {test.concept_name}")
```

## Best Practices

### 1. Always Use Standard Concepts for Analysis
```python
# ✅ Good - filters to standard concepts
results = client.vocab.search("diabetes", standard_concept="S")

# ❌ Avoid - includes non-standard concepts
results = client.vocab.search("diabetes")  # No filter
```

### 2. Batch API Calls When Possible
```python
# ✅ Good - single API call
concepts = client.vocab.bulk_get([201826, 1503297, 4548])

# ❌ Inefficient - multiple API calls
concepts = []
for concept_id in [201826, 1503297, 4548]:
    concepts.append(client.vocab.get_concept(concept_id))
```

### 3. Use Hierarchies Appropriately
```python
# For inclusive cohorts (recommended)
diabetes_concept_id = 201826
all_diabetes_types = client.vocab.descendants(diabetes_concept_id)

# Use all descendants in your cohort definition
concept_set = {
    "id": 0,
    "name": "All Diabetes Types", 
    "expression": {
        "items": [{"concept": {"conceptId": diabetes_concept_id, "includeDescendants": True}}]
    }
}
```

## Common Workflows

### Building a Concept Set for Research

1. **Search** for your concept of interest
2. **Review** the results and pick the most appropriate standard concept
3. **Check descendants** to see if you want to include more specific concepts
4. **Validate** by looking at the concept names and classifications

```python
# Complete workflow example
def build_diabetes_concept_set():
    # Step 1: Search
    results = client.vocab.search("type 2 diabetes", domain_id="Condition", standard_concept="S")
    
    # Step 2: Review and select
    main_concept = results[0]  # Assume first is best match
    print(f"Selected: {main_concept.concept_name}")
    
    # Step 3: Check descendants
    descendants = client.vocab.concept_descendants(main_concept.concept_id)
    print(f"This will include {len(descendants)} related concepts")
    
    # Step 4: Create concept set definition
    concept_set = {
        "id": 0,
        "name": "Type 2 Diabetes",
        "expression": {
            "items": [{
                "concept": {
                    "conceptId": main_concept.concept_id,
                    "includeDescendants": True  # Include all subtypes
                }
            }]
        }
    }
    
    return concept_set
```

## API Method Reference

### REST Endpoint to Python Method Mapping

The vocabulary service follows a predictable naming pattern that mirrors the REST API endpoints:

| REST Endpoint | Python Method | Description |
|--------------|---------------|-------------|
| `/vocabulary/domains` | `list_domains()` | Get all available domains |
| `/vocabulary/vocabularies` | `list_vocabularies()` | Get all available vocabularies |
| `/vocabulary/concept/{id}` | `concept(id)` | Get a single concept |
| `/vocabulary/concept/{id}/descendants` | `concept_descendants(id)` | Get child concepts |
| `/vocabulary/concept/{id}/related` | `concept_related(id)` | Get related concepts |
| Bulk concept lookup | `concepts(ids)` | Get multiple concepts |

### Backwards Compatibility

For backwards compatibility, these legacy method names are still supported:
- `descendants()` → Use `concept_descendants()` instead
- `related()` → Use `concept_related()` instead  
- `bulk_get()` → Use `concepts()` instead

### Method Details

All methods return Pydantic models with proper type hints and validation. Most methods support caching via the `@cached_method` decorator for improved performance.

## Error Handling

```python
from ohdsi_webapi.exceptions import WebApiError

try:
    concept = client.vocab.get_concept(999999999)  # Invalid ID
except WebApiError as e:
    print(f"API Error: {e.status_code} - {e.message}")
    # Handle gracefully - maybe use a default concept or ask user to try again
```

## Performance Tips

1. **Cache frequently used concepts** in your application
2. **Use bulk operations** when fetching multiple concepts
3. **Apply filters early** to reduce result set sizes
4. **Reuse search results** instead of re-searching

## Next Steps

- **[Concept Sets](concept_sets.md)**: Learn how to group concepts for analysis
- **[Cohorts](cohorts.md)**: Use concepts to define patient populations  
- **[Caching](caching.md)**: Optimize performance for repeated API calls

Need help? The OHDSI community is very welcoming to newcomers. Check out the [OHDSI Forums](https://forums.ohdsi.org/) for questions and discussions.
