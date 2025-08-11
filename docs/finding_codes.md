# Finding the Right OMOP Concept Codes

One of the most critical aspects of working with OHDSI data is finding the right OMOP concept codes for your research. Medical terminology is complex, and terms like "cardiovascular disease" or "diabetes" can match dozens or hundreds of specific conditions.

This guide shows you exactly how to discover, evaluate, and choose the right concept codes using the OHDSI WebAPI client.

## The Challenge

When researchers ask for:
- **"Cardiovascular disease"** → Could match 200+ concepts
- **"Diabetes"** → Type 1, Type 2, gestational, secondary diabetes
- **"Cancer"** → Hundreds of specific cancer types
- **"Heart failure"** → Acute, chronic, left-sided, right-sided variants

Without guidance, it's easy to choose concepts that are too broad (millions of patients) or too narrow (dozens of patients).

## The Solution: Systematic Code Discovery

### Step 1: Search for Concepts

Start by searching for your medical term of interest:

```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# Search for all concepts matching your term
concepts = client.vocabulary.search("cardiovascular")
print(f"Found {len(concepts)} concepts matching 'cardiovascular'")
```

This returns **all OMOP concepts** that match your search term - could be hundreds!

### Step 2: Filter to Medical Conditions

Most of the time, you want actual medical conditions (not drugs, procedures, etc.):

```python
# Filter to condition concepts only
conditions = [c for c in concepts 
             if c.domain_id == 'Condition' and c.standard_concept == 'S']

print(f"Filtered to {len(conditions)} standard condition concepts")

# Show the top results
for i, concept in enumerate(conditions[:5]):
    print(f"{i+1}. ID {concept.concept_id}: {concept.concept_name}")
    print(f"   Domain: {concept.domain_id}, Standard: {concept.standard_concept}")
```

### Step 3: Understand Concept Scope

This is the **critical step** - understanding how broad or narrow each concept is:

```python
# Check how many subtypes each concept includes
for concept in conditions[:5]:
    descendants = client.vocabulary.concept_descendants(concept.concept_id)
    print(f"{concept.concept_name}:")
    print(f"  → Includes {len(descendants)} more specific conditions")
    
    # Show examples of what's included
    if descendants:
        examples = [d.concept_name for d in descendants[:3]]
        print(f"  → Examples: {', '.join(examples)}")
        if len(descendants) > 3:
            print(f"  → ...and {len(descendants) - 3} more")
    print()
```

**Example output:**
```
Cardiovascular disease:
  → Includes 1,247 more specific conditions
  → Examples: Acute myocardial infarction, Heart failure, Stroke
  → ...and 1,244 more

Hypertensive heart disease:
  → Includes 23 more specific conditions
  → Examples: Hypertensive heart failure, Hypertensive cardiomegaly
  → ...and 21 more

Acute myocardial infarction:
  → Includes 8 more specific conditions
  → Examples: STEMI, NSTEMI, Inferior MI
  → ...and 5 more
```

### Step 4: Search for Specific Conditions

Often you want specific, well-known conditions rather than broad categories:

```python
# Search for specific cardiovascular conditions
specific_searches = [
    "myocardial infarction",    # Heart attack
    "heart failure",            # Heart failure
    "atrial fibrillation",      # A-fib
    "cerebrovascular accident", # Stroke
    "coronary artery disease"   # CAD
]

specific_codes = {}

for search_term in specific_searches:
    search_results = client.vocabulary.search(search_term)
    
    # Find the best standard condition concept
    best_match = None
    for concept in search_results:
        if (concept.domain_id == 'Condition' and 
            concept.standard_concept == 'S' and
            search_term.lower() in concept.concept_name.lower()):
            best_match = concept
            break
    
    if best_match:
        specific_codes[search_term] = best_match
        print(f"✅ {search_term.title()}: {best_match.concept_id}")
        print(f"   {best_match.concept_name}")
```

### Step 5: Validate Concept Size with Real Data

Before finalizing your concept choices, check how many patients they would include:

```python
def check_concept_size(concept_id: int, source_key: str):
    """Check how many patients a concept would include"""
    
    # Note: This is an advanced example showing the general approach.
    # In practice, you would create concept sets and cohorts through the WebAPI
    # to get actual patient counts for validation.
    
    print(f"To validate concept {concept_id}:")
    print("1. Create a concept set with this concept")
    print("2. Build a cohort using that concept set")
    print("3. Generate the cohort against your data source")
    print("4. Check the resulting patient count")
    print("5. Adjust concept selection based on results")
    
    # For the specific implementation, see the cohorts documentation
    return "See cohorts documentation for complete workflow"

# Example of concept validation approach
sources = client.sources()
source_key = sources[0].source_key if sources else "EUNOMIA"

for concept in conditions[:3]:
    print(f"\\n{concept.concept_name} (ID: {concept.concept_id})")
    print("  → Use this concept in a test cohort to validate size")
    
    descendants = client.vocabulary.concept_descendants(concept.concept_id)
    if len(descendants) > 1000:
        print("  ⚠️  Very broad - consider more specific subtypes")
    elif len(descendants) < 5:
        print("  ⚠️  Very narrow - consider broader category")
    else:
        print("  ✓  Good scope for analysis")
```

## Common Cardiovascular Disease Codes

Based on typical research needs, here are the most commonly used cardiovascular concept codes:

| **Condition** | **Concept ID** | **Scope** | **Use Case** |
|---------------|----------------|-----------|--------------|
| Cardiovascular disease | 194990 | Very broad (1,200+ subtypes) | Population health studies |
| Myocardial infarction | 4329847 | Specific (heart attacks) | Acute care research |
| Heart failure | 444094 | Specific | Chronic disease management |
| Cerebrovascular accident | 381591 | Specific (strokes) | Neurological outcomes |
| Coronary artery disease | 4110056 | Specific | Interventional cardiology |
| Atrial fibrillation | 313217 | Specific | Arrhythmia studies |
| Hypertensive heart disease | 316866 | Moderately broad | Hypertension complications |

## Decision Framework

### Choose **BROAD concepts** when:
- ✅ Population health studies
- ✅ Exploring overall disease burden
- ✅ Screening for exclusion criteria
- ✅ You want to capture all cardiovascular conditions

**Example:** Use concept 194990 (Cardiovascular disease) with `include_descendants=True`

### Choose **SPECIFIC concepts** when:
- ✅ Clinical trial recruitment
- ✅ Studying specific interventions
- ✅ Comparing outcomes between condition types
- ✅ You need precise case definitions

**Example:** Use concept 4329847 (Myocardial infarction) for heart attack studies

### Choose **MULTIPLE specific concepts** when:
- ✅ You want specific conditions but more than one type
- ✅ Building custom disease definitions
- ✅ Comparing related but distinct conditions

**Example:** Combine concepts 4329847 (MI) + 444094 (Heart failure) + 381591 (Stroke)

## Practical Example: Building a Cardiovascular Cohort

Here's a complete example showing the decision process:

```python
def build_cardiovascular_cohort():
    """Complete example of finding and using cardiovascular codes"""
    
    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
    
    # Step 1: Explore options
    concepts = client.vocabulary.search("cardiovascular")
    conditions = [c for c in concepts if c.domain_id == 'Condition' and c.standard_concept == 'S']
    
    print("Available cardiovascular concepts:")
    for concept in conditions[:3]:
        descendants = client.vocabulary.concept_descendants(concept.concept_id)
        print(f"  {concept.concept_id}: {concept.concept_name} ({len(descendants)} subtypes)")
    
    # Step 2: Choose based on research question
    
    # Option A: Broad cardiovascular disease study
    print("\\nOption A: Use broad cardiovascular disease concept")
    broad_concept_id = 194990  # Cardiovascular disease
    broad_descendants = client.vocabulary.concept_descendants(broad_concept_id)
    print(f"Concept {broad_concept_id} includes {len(broad_descendants)} subtypes")
    
    # Option B: Specific major cardiovascular events
    print("\\nOption B: Use specific cardiovascular events")
    major_events = [
        (4329847, "Myocardial infarction"),
        (444094, "Heart failure"),
        (381591, "Cerebrovascular accident")
    ]
    
    for concept_id, name in major_events:
        descendants = client.vocabulary.concept_descendants(concept_id)
        print(f"  {name} ({concept_id}): {len(descendants)} subtypes")
    
    # Step 3: Create concept sets for use in cohorts
    print("\\nTo create cohorts with these concepts:")
    print("1. Use conceptset.create() to build concept sets")
    print("2. Use cohortdefinition.create() to build cohorts")
    print("3. See the cohorts documentation for complete workflow")
    
    return conditions

# Example usage
cardiovascular_concepts = build_cardiovascular_cohort()
```

## Best Practices

1. **Always explore first** - Use search and descendant queries to understand scope
2. **Validate with real data** - Check patient counts before finalizing concepts
3. **Document your choices** - Record which concepts you included/excluded and why
4. **Start broad, then narrow** - Begin with broad concepts, then refine based on results
5. **Consider your research question** - Population health = broad, clinical trials = specific
6. **Test multiple approaches** - Compare broad vs specific to understand the impact
7. **Use clinical expertise** - Involve clinicians in concept selection decisions

## Interactive Code Discovery Tool

Here's a helper function you can use to interactively explore concepts:

```python
def explore_medical_concept(search_term: str):
    """Interactive tool to explore medical concepts"""
    
    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
    
    print(f"🔍 Exploring: '{search_term}'")
    print("=" * 50)
    
    # Search and filter
    concepts = client.vocabulary.search(search_term)
    conditions = [c for c in concepts if c.domain_id == 'Condition' and c.standard_concept == 'S']
    
    print(f"Found {len(conditions)} condition concepts:")
    
    # Show options with scope
    for i, concept in enumerate(conditions[:10]):
        descendants = client.vocabulary.concept_descendants(concept.concept_id)
        print(f"\\n{i+1}. {concept.concept_name}")
        print(f"    ID: {concept.concept_id}")
        print(f"    Scope: {len(descendants)} descendant conditions")
        
        if len(descendants) <= 5:
            for desc in descendants:
                print(f"      → {desc.concept_name}")
        elif descendants:
            for desc in descendants[:3]:
                print(f"      → {desc.concept_name}")
            print(f"      → ...and {len(descendants) - 3} more")
    
    return conditions

# Usage examples:
# explore_medical_concept("diabetes")
# explore_medical_concept("cancer") 
# explore_medical_concept("cardiovascular")
# explore_medical_concept("mental health")
```

This systematic approach ensures you choose the right concept codes for your specific research needs, avoiding the common pitfalls of overly broad or narrow definitions.
