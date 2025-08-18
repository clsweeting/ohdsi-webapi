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

### Vocabulary = "Where did this code come from?"

**Vocabulary** tells you the source coding system:
- `SNOMED` - from SNOMED CT
- `RxNorm` - from RxNorm  
- `ICD10CM` - from ICD-10-CM

### Domain = "What type of medical concept is this?"

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

### Why this matters

When building cohorts, you search by **domain** ("show me all conditions") but the results might come from multiple **vocabularies** (SNOMED, ICD-10, etc.).

-----------------------


## OMOP Database Structure

The vocabulary data lives in these key tables:

| Table | What It Contains |
|-------|------------------|
| `VOCABULARY` | List of all coding systems (SNOMED, RxNorm, etc.) |
| `CONCEPT` | All medical concepts from all vocabularies |
| `CONCEPT_RELATIONSHIP` | How concepts relate to each other |
| `CONCEPT_ANCESTOR` | Parent/child hierarchies (e.g., "diabetes" → "type 2 diabetes") |

## Working with the Vocabulary API

Setup

```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
```

### 1. Looking Up a Specific Concept

If you know the concept ID:

```python
# Get a specific concept by ID
concept = client.vocabulary.concept(201826)  # Type 2 diabetes

print(f"Name: {concept.concept_name}")
print(f"Domain: {concept.domain_id}")  
print(f"Vocabulary: {concept.vocabulary_id}")
print(f"Standard: {concept.standard_concept}")
```

### 2. Searching for Concepts by Text

This is usually how you start - you know what you're looking for but need the concept ID:

```python
# Search for diabetes-related concepts
results = client.vocabulary.search(
    query="diabetes",
    domain_id="Condition",        # Only conditions
    standard_concept="S",         # Only standard concepts
    page_size=100                 # Default page size (increased from 20 for better UX)
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
- `page_size` - Results per page (default: 100). Larger defaults help users discover pagination exists
- `page` - Which page of results to receive

**Pagination Tip**: The default page size is 100 to make pagination more obvious. If you get exactly 100 results, there are likely more - use `page=2` to get the next batch.


### 3. Working with Concept Hierarchies

Medical concepts are organized in hierarchies. For example:
- Diabetes (parent)
  - Type 1 diabetes (child)
  - Type 2 diabetes (child)

```python
# Get all child concepts (more specific) - predictable naming
children = client.vocabulary.concept_descendants(201826)  # All types of diabetes
print(f"Found {len(children)} more specific diabetes concepts")

# Get all related concepts - predictable naming
related = client.vocabulary.concept_related(201826)  # Related concepts
print(f"Found {len(related)} related concepts")
```

**When to use hierarchies:**
- Descendants: When you want to be inclusive (e.g., find all types of diabetes)
- Related: When you want to find mapped or associated concepts


### 4. Bulk Operations

When you have multiple concept IDs, batch them for better performance:

```python
concept_ids = [201826, 1503297, 3004410]  # diabetes, metformin, hemoglobin A1c

# The concepts() method uses reliable individual calls
concepts = client.vocabulary.concepts(concept_ids)

for concept in concepts:
    print(f"{concept.concept_id}: {concept.concept_name} ({concept.domain_id})")
```

**⚠️ Important**: Use OMOP **concept IDs** (integers) like `201826`, not source **concept codes** like `"4548-4"`. The concepts() method expects numeric OMOP concept IDs.

**💡 If you have source codes**: Use `lookup_identifiers()` to convert source codes to OMOP concept IDs:
```python
# Convert LOINC codes to OMOP concepts  
loinc_codes = [("4548-4", "LOINC"), ("33747-0", "LOINC")]  # A1c, Anion gap
concepts = client.vocabulary.lookup_identifiers(loinc_codes)
concept_ids = [c.concept_id for c in concepts]  # Now you have OMOP IDs
```

**Note**: If `lookup_identifiers()` has issues with your WebAPI version, you can search for codes individually:
```python
# Alternative: search for specific codes
diabetes_icd = client.vocabulary.search("E11.9", vocabulary_id="ICD10CM", page_size=10)
metformin_ndc = client.vocabulary.search("50096", vocabulary_id="NDC", page_size=10)
```

### 5. Converting Source Codes to OMOP Concepts

When you have codes from other systems (like ICD-10 or NDC codes), you need to map them to OMOP concepts:

```python
# Method 1: Try bulk lookup (may not work on all WebAPI versions)
try:
    lookup_results = client.vocabulary.lookup_identifiers([
        ("E11.9", "ICD10CM"),   # ICD-10 code (using tuple format)
        ("50096", "NDC"),       # NDC drug code
    ])
    print(f"Found {len(lookup_results)} concepts via bulk lookup")
except Exception as e:
    print(f"Bulk lookup failed: {e}")
    # Fallback to individual searches (see Method 2)

# Method 2: Individual searches (more reliable)
codes_to_lookup = [
    ("E11.9", "ICD10CM", "Type 2 diabetes"),
    ("50096", "NDC", "Metformin tablet"),
]

found_concepts = []
for code, vocab, description in codes_to_lookup:
    results = client.vocabulary.search(code, vocabulary_id=vocab, page_size=10)
    # Look for exact code match
    exact_match = next((c for c in results if c.concept_code == code), None)
    if exact_match:
        found_concepts.append(exact_match)
        print(f"✓ {code} → {exact_match.concept_id}: {exact_match.concept_name}")
    else:
        print(f"✗ {code} not found in {vocab}")
```


### 6. Exploring Available Domains and Vocabularies

To see what types of medical data are available:

```python
# List all domains (Condition, Drug, Procedure, etc.)
domains = client.vocabulary.domains()
for domain in domains:
    print(f"{domain['domainId']}: {domain['domainName']}")
```

To see what vocabularies (coding systems) are available:

```python
# List all vocabularies (SNOMED, RxNorm, ICD-10, etc.)
vocabularies = client.vocabulary.vocabularies()
for vocab in vocabularies:
    print(f"{vocab['vocabularyId']}: {vocab['vocabularyName']}")
```


