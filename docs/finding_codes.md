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

client = WebApiClient()

# Search for all concepts matching your term
concepts = await client.vocabulary.search("cardiovascular")
print(f"Found {len(concepts)} concepts matching 'cardiovascular'")
```

This returns **all OMOP concepts** that match your search term - could be hundreds!

### Step 2: Filter to Medical Conditions

Most of the time, you want actual medical conditions (not drugs, procedures, etc.):

```python
# Filter to condition concepts only
conditions = [c for c in concepts 
             if c.domainId == 'Condition' and c.standardConcept == 'S']

print(f"Filtered to {len(conditions)} standard condition concepts")

# Show the top results
for i, concept in enumerate(conditions[:5]):
    print(f"{i+1}. ID {concept.concept_id}: {concept.concept_name}")
    print(f"   Domain: {concept.domainId}, Standard: {concept.standardConcept}")
```

### Step 3: Understand Concept Scope

This is the **critical step** - understanding how broad or narrow each concept is:

```python
# Check how many subtypes each concept includes
for concept in conditions[:5]:
    descendants = await client.vocabulary.descendants(concept.concept_id)
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
    search_results = await client.vocabulary.search(search_term)
    
    # Find the best standard condition concept
    best_match = None
    for concept in search_results:
        if (concept.domainId == 'Condition' and 
            concept.standardConcept == 'S' and
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
async def check_concept_size(concept_id: int, source_key: str):
    """Check how many patients a concept would include"""
    
    # Create test concept set
    test_cs = client.cohorts.create_concept_set(concept_id, "Test Concept")
    
    # Create minimal cohort to get counts
    from ohdsi_webapi.models.cohort import CohortDefinition
    test_cohort = CohortDefinition(
        name="Concept Size Test",
        expression=client.cohorts.create_base_cohort_expression([test_cs])
    )
    
    # Generate and get counts
    created = await client.cohorts.create(test_cohort)
    await client.cohorts.generate(created.id, source_key)
    await client.cohorts.poll_generation(created.id, source_key)
    counts = await client.cohorts.counts(created.id)
    
    patient_count = counts[0].subject_count if counts else 0
    
    # Clean up
    await client.cohorts.delete(created.id)
    
    return patient_count

# Test different concept options
sources = await client.sources.list()
source_key = sources[0].source_key

for concept in conditions[:3]:
    count = await check_concept_size(concept.concept_id, source_key)
    print(f"{concept.concept_name}: {count:,} patients")
    
    if count > 100000:
        print("  ⚠️  Very broad - consider more specific subtypes")
    elif count < 100:
        print("  ⚠️  Very narrow - consider broader category")
    else:
        print("  ✓  Good size for analysis")
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
async def build_cardiovascular_cohort():
    """Complete example of finding and using cardiovascular codes"""
    
    client = WebApiClient()
    
    # Step 1: Explore options
    concepts = await client.vocabulary.search("cardiovascular")
    conditions = [c for c in concepts if c.domainId == 'Condition' and c.standardConcept == 'S']
    
    print("Available cardiovascular concepts:")
    for concept in conditions[:3]:
        descendants = await client.vocabulary.descendants(concept.concept_id)
        print(f"  {concept.concept_id}: {concept.concept_name} ({len(descendants)} subtypes)")
    
    # Step 2: Choose based on research question
    
    # Option A: Broad cardiovascular disease study
    broad_cs = client.cohorts.create_concept_set(
        concept_id=194990,  # Cardiovascular disease
        name="All Cardiovascular Disease",
        include_descendants=True  # Include all 1,200+ subtypes
    )
    
    # Option B: Specific major cardiovascular events
    major_events = [
        (4329847, "Myocardial infarction"),
        (444094, "Heart failure"),
        (381591, "Cerebrovascular accident")
    ]
    
    specific_concept_sets = []
    for concept_id, name in major_events:
        cs = client.cohorts.create_concept_set(concept_id, name)
        specific_concept_sets.append(cs)
    
    # Step 3: Test with real data
    sources = await client.sources.list()
    source_key = sources[0].source_key
    
    # Compare broad vs specific approaches
    print("\\nPatient counts comparison:")
    
    # Broad approach
    broad_results = await client.cohorts.build_incremental_cohort(
        source_key=source_key,
        base_name="Broad CVD Study",
        concept_sets=[broad_cs],
        filters=[{"type": "age", "min_age": 18}]
    )
    print(f"Broad CVD: {broad_results[-1][1]:,} patients")
    
    # Specific approach
    for cs, (concept_id, name) in zip(specific_concept_sets, major_events):
        specific_results = await client.cohorts.build_incremental_cohort(
            source_key=source_key,
            base_name=f"Specific: {name}",
            concept_sets=[cs],
            filters=[{"type": "age", "min_age": 18}]
        )
        print(f"{name}: {specific_results[-1][1]:,} patients")
    
    return broad_cs, specific_concept_sets
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
async def explore_medical_concept(search_term: str):
    """Interactive tool to explore medical concepts"""
    
    client = WebApiClient()
    
    print(f"🔍 Exploring: '{search_term}'")
    print("=" * 50)
    
    # Search and filter
    concepts = await client.vocabulary.search(search_term)
    conditions = [c for c in concepts if c.domainId == 'Condition' and c.standardConcept == 'S']
    
    print(f"Found {len(conditions)} condition concepts:")
    
    # Show options with scope
    for i, concept in enumerate(conditions[:10]):
        descendants = await client.vocabulary.descendants(concept.concept_id)
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
# await explore_medical_concept("diabetes")
# await explore_medical_concept("cancer") 
# await explore_medical_concept("cardiovascular")
# await explore_medical_concept("mental health")
```

This systematic approach ensures you choose the right concept codes for your specific research needs, avoiding the common pitfalls of overly broad or narrow definitions.
