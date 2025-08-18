## Advanced Filter Types

Beyond basic demographics and conditions, the cohort builder supports advanced clinical filters for sophisticated study designs:

### Data Quality & Enrollment Filters

#### Observation Period Requirements
Ensure patients have continuous health data coverage:

```python
# Require 1 year of prior data and 6 months of follow-up
expression = client.cohortdefs.add_observation_period_filter(
    expression,
    days_before=365,  # 1 year of prior data
    days_after=180,  # 6 months of follow-up data
    filter_name="Continuous enrollment (1yr prior, 6mo follow-up)"
)
```

#### Prior Observation Requirements  
Ensure minimum data history for baseline characterization:

```python
# Require at least 2 years of prior observation
expression = client.cohortdefs.add_prior_observation_filter(
    expression,
    min_days=730,  # 2 years
    filter_name="Minimum 2 years prior data"
)
```

### Healthcare Utilization Filters

#### Visit Type Requirements
Filter by type of healthcare encounter:

```python
# Common visit types (use OMOP concept IDs)
VISIT_TYPES = {
    9201: "Inpatient visit",
    9202: "Outpatient visit",
    9203: "Emergency room visit",
    9204: "Intensive care",
    8717: "Telehealth visit"
}

# Require outpatient visit in last 90 days
expression = client.cohortdefs.add_visit_filter(
    expression,
    visit_concept_ids=[9202],  # Outpatient
    days_before=90,
    filter_name="Outpatient visit in last 90 days"
)

# Require either inpatient OR ER visit in last 30 days
expression = client.cohortdefs.add_visit_filter(
    expression,
    visit_concept_ids=[9201, 9203],  # Inpatient OR ER
    days_before=30,
    filter_name="Hospital or ER visit in last 30 days"
)
```

### Laboratory & Measurement Filters

#### Lab Value Requirements
Filter by specific lab results and value ranges:

```python
# HbA1c between 7-10% in last 6 months
hba1c_cs = client.cohortdefs.create_concept_set(3655963, "Hemoglobin A1c")
expression = client.cohortdefs.add_measurement_filter(
    expression,
    concept_set_id=1,  # HbA1c concept set index
    value_min=7.0,
    value_max=10.0,
    days_before=180,  # Last 6 months
    filter_name="HbA1c 7-10% (last 6 months)"
)

# LDL cholesterol > 100 mg/dL
ldl_cs = client.cohortdefs.create_concept_set(3004249, "LDL Cholesterol")
expression = client.cohortdefs.add_measurement_filter(
    expression,
    concept_set_id=2,
    value_min=100.0,  # No upper limit
    days_before=365,
    filter_name="LDL > 100 mg/dL (last year)"
)

# Blood pressure measurements (any value) 
bp_cs = client.cohortdefs.create_concept_set(3027018, "Systolic Blood Pressure")
expression = client.cohortdefs.add_measurement_filter(
    expression,
    concept_set_id=3,
    # No value limits - just require measurement exists
    days_before=90,
    filter_name="BP measurement in last 90 days"
)
```

#### Common Lab Value Examples

```python
# Diabetes monitoring labs
HBA1C_RANGES = {
    "controlled": (0, 7.0),      # < 7%
    "moderate": (7.0, 9.0),      # 7-9%  
    "uncontrolled": (9.0, None)  # > 9%
}

# Kidney function
EGFR_STAGES = {
    "normal": (90, None),        # ≥ 90 mL/min/1.73m²
    "mild_ckd": (60, 89),        # 60-89 
    "moderate_ckd": (30, 59),    # 30-59
    "severe_ckd": (15, 29),      # 15-29
    "kidney_failure": (0, 14)    # < 15
}

# Lipid management
CHOLESTEROL_TARGETS = {
    "ldl_high_risk": (0, 70),    # < 70 mg/dL for high risk
    "ldl_moderate": (70, 100),   # 70-100 mg/dL
    "ldl_elevated": (100, None)  # > 100 mg/dL
}
```

### Medication Usage Filters

#### Drug Era Requirements
Filter by continuous medication exposure periods:

```python
# Metformin for at least 90 days in last year
metformin_cs = client.cohortdefs.create_concept_set(1502826, "Metformin")
expression = client.cohortdefs.add_drug_era_filter(
    expression,
    concept_set_id=4,  # Metformin concept set
    era_length_min=90,  # At least 90 days continuous
    days_before=365,  # Within last year
    filter_name="Metformin ≥90 days (last year)"
)

# Any statin for at least 180 days
statin_cs = client.cohortdefs.create_concept_set(1539403, "Statin", include_descendants=True)
expression = client.cohortdefs.add_drug_era_filter(
    expression,
    concept_set_id=5,
    era_length_min=180,  # 6 months minimum
    days_before=730,  # Within last 2 years
    filter_name="Statin therapy ≥180 days"
)

# No minimum duration - just any exposure
ace_inhibitor_cs = client.cohortdefs.create_concept_set(1308216, "ACE Inhibitors", True)
expression = client.cohortdefs.add_drug_era_filter(
    expression,
    concept_set_id=6,
    # era_length_min not specified = any duration
    days_before=90,
    filter_name="ACE inhibitor in last 90 days"
)
```

### Complex Logic Filters

#### Multiple Conditions Requirements
Apply ALL or ANY logic across multiple conditions:

```python
# Must have BOTH hypertension AND diabetes
hypertension_cs = client.cohortdefs.create_concept_set(316866, "Hypertensive disease")
diabetes_cs = client.cohortdefs.create_concept_set(201826, "Type 2 diabetes")

expression = client.cohortdefs.add_multiple_conditions_filter(
    expression,
    concept_set_ids=[7, 8],  # Hypertension and diabetes concept sets
    logic="ALL",  # Must have BOTH conditions
    days_before=1095,  # Within last 3 years
    filter_name="Hypertension AND diabetes (last 3 years)"
)

# Must have ANY cardiovascular condition
mi_cs = client.cohortdefs.create_concept_set(4329847, "Myocardial infarction")
stroke_cs = client.cohortdefs.create_concept_set(381591, "Cerebrovascular accident")
hf_cs = client.cohortdefs.create_concept_set(444094, "Heart failure")

expression = client.cohortdefs.add_multiple_conditions_filter(
    expression,
    concept_set_ids=[9, 10, 11],  # MI, stroke, or HF
    logic="ANY",  # Just need ONE of these
    days_before=1825,  # Within last 5 years
    filter_name="Any major CVD event (last 5 years)"
)
```

### Real-World Clinical Study Example

```python
async def comprehensive_diabetes_study():
    """Real-world example combining all filter types"""

    client = WebApiClient()

    # Define all concept sets needed
    concept_sets = [
        client.cohortdefs.create_concept_set(201826, "Type 2 Diabetes"),  # 0
        client.cohortdefs.create_concept_set(3655963, "Hemoglobin A1c"),  # 1
        client.cohortdefs.create_concept_set(1502826, "Metformin"),  # 2
        client.cohortdefs.create_concept_set(316866, "Hypertensive disease"),  # 3
        client.cohortdefs.create_concept_set(314666, "Chronic kidney disease"),  # 4
        client.cohortdefs.create_concept_set(443392, "Malignant neoplasm")  # 5 - Cancer
    ]

    # Inclusion criteria (what we want)
    inclusion_filters = [
        # Demographics & data quality
        {"type": "age", "min_age": 40, "max_age": 75, "name": "Age 40-75"},
        {"type": "prior_observation", "min_days": 365, "name": "≥1 year prior data"},
        {"type": "observation_period", "days_before": 365, "days_after": 180,
         "name": "Continuous enrollment (1yr prior, 6mo follow-up)"},

        # Clinical criteria  
        {"type": "time_window", "concept_set_id": 0, "days_before": 730,
         "filter_name": "Diabetes diagnosis (last 2 years)"},

        # Lab requirements
        {"type": "measurement", "concept_set_id": 1, "value_min": 7.0, "value_max": 10.0,
         "days_before": 180, "filter_name": "HbA1c 7-10% (last 6 months)"},

        # Medication requirements
        {"type": "drug_era", "concept_set_id": 2, "era_length_min": 90,
         "days_before": 365, "filter_name": "Metformin ≥90 days (last year)"},

        # Healthcare utilization
        {"type": "visit", "visit_concept_ids": [9202], "days_before": 90,
         "filter_name": "Outpatient visit (last 90 days)"},

        # Comorbidity requirements  
        {"type": "multiple_conditions", "concept_set_ids": [3, 4], "logic": "ALL",
         "days_before": 1095, "filter_name": "Hypertension AND kidney disease"}
    ]

    # Exclusion criteria (what we don't want)
    exclusions = [
        {"type": "condition", "concept_set_id": 5, "days_before": 1825,
         "name": "No cancer history (5 years)"},
        {"type": "death", "days_after_index": 30,
         "name": "Survived ≥30 days"}
    ]

    # Build comprehensive cohort
    results = await client.cohortdefs.build_incremental_cohort(
        source_key="your_source",
        base_name="Comprehensive Diabetes Study",
        concept_sets=concept_sets,
        filters=inclusion_filters,
        exclusions=exclusions
    )

    return results
```

### Advanced Filter Reference

| Filter Type | Purpose | Key Parameters | Example Use Case |
|-------------|---------|----------------|------------------|
| `observation_period` | Data continuity | `days_before`, `days_after` | Ensure 1yr baseline + 6mo follow-up |
| `prior_observation` | Data quality | `min_days` | Require 2+ years of health records |
| `visit` | Care utilization | `visit_concept_ids`, `days_before` | Recent outpatient engagement |
| `measurement` | Lab values | `value_min`, `value_max`, `days_before` | HbA1c 7-10% in last 6 months |
| `drug_era` | Medication adherence | `era_length_min`, `days_before` | Metformin for 90+ days |
| `multiple_conditions` | Complex comorbidity | `concept_set_ids`, `logic` | Diabetes AND hypertension |

These advanced filters enable creation of clinically sophisticated cohorts that match real-world research study inclusion/exclusion criteria. They're essential for pragmatic clinical trials, comparative effectiveness research, and quality improvement studies.

## Handling Broad Medical Terms

### The Challenge: "Cardiovascular Disease"

When users ask for broad terms like "cardiovascular disease", "diabetes", or "cancer", these can match dozens or hundreds of specific conditions. Here's how to handle this systematically:

#### 1. Search and Explore First

```python
async def explore_cardiovascular_concepts():
    """Explore what 'cardiovascular disease' actually includes"""
    
    from ohdsi_webapi import WebApiClient
    
    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
    
    # Search for cardiovascular concepts
    cvd_concepts = await client.vocabulary.search("cardiovascular disease")
    
    print(f"Found {len(cvd_concepts)} concepts for 'cardiovascular disease':")
    for concept in cvd_concepts[:10]:  # Show first 10
        print(f"  {concept.concept_id}: {concept.concept_name}")
        print(f"    Domain: {concept.domain_id}, Standard: {concept.standard_concept}")
    
    # Look for high-level parent concepts
    high_level = [c for c in cvd_concepts if "disease" in c.concept_name.lower() 
                  and len(c.concept_name.split()) <= 4]
    
    print(f"\nHigh-level CVD concepts ({len(high_level)}):")
    for concept in high_level:
        print(f"  {concept.concept_id}: {concept.concept_name}")
        
        # Check descendants to see scope
        descendants = await client.vocabulary.descendants(concept.concept_id)
        print(f"    → {len(descendants)} descendant conditions")

# Example output:
# Found 247 concepts for 'cardiovascular disease'
#   194990: Cardiovascular disease
#     Domain: Condition, Standard: S
#     → 1,247 descendant conditions
#   313217: Hypertensive heart disease  
#     Domain: Condition, Standard: S
#     → 23 descendant conditions
```

#### 2. Let Users Choose Specificity

```python
async def build_cvd_cohort_with_options():
    """Give users multiple options for cardiovascular disease"""

    from ohdsi_webapi import WebApiClient
    from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

    # Option 1: Very broad - all cardiovascular disease
    def create_concept_set(concept_id: int, name: str, include_descendants: bool = True):
        # Note: In real usage, you'd fetch full concept details from vocabulary
        concept = Concept(
            concept_id=concept_id,
            concept_name=name,
            standard_concept="S",
            domain_id="Condition"
        )

        item = ConceptSetItem(
            concept=concept,
            include_descendants=include_descendants,
            include_mapped=False,
            is_excluded=False
        )

        return ConceptSetExpression(items=[item])

    broad_cvd = create_concept_set(194990, "All Cardiovascular Disease", True)

    # Option 2: Specific conditions only
    specific_conditions = [
        (4329847, "Myocardial infarction"),
        (381591, "Cerebrovascular accident"),
        (4110056, "Chronic ischemic heart disease"),
        (316866, "Hypertensive heart disease")
    ]

    # Create separate concept sets for each
    specific_concept_sets = []
    for concept_id, name in specific_conditions:
        cs = create_concept_set(concept_id, name, True)
        specific_concept_sets.append(cs)

    # Option 3: Let user see counts for different approaches
    sources = client.source.sources()
    source_key = sources[0].source_key

    print("🔍 Cardiovascular Disease Cohort Options:")
    print("=" * 50)

    # Test broad approach
    broad_filters = [{"type": "gender", "gender": "male"}, {"type": "age", "min_age": 40}]
    broad_results = await client.cohortdefs.build_incremental_cohort(
        source_key=source_key,
        base_name="Broad CVD (All types)",
        concept_sets=[broad_cvd],
        filters=broad_filters
    )

    print(f"📊 BROAD: All CVD types → {broad_results[-1][1]:,} patients")

    # Test specific approach
    for i, (cs, (concept_id, name)) in enumerate(zip(specific_concept_sets, specific_conditions)):
        specific_results = await client.cohortdefs.build_incremental_cohort(
            source_key=source_key,
            base_name=f"Specific: {name}",
            concept_sets=[cs],
            filters=broad_filters
        )
        print(f"📊 SPECIFIC: {name} → {specific_results[-1][1]:,} patients")

    return broad_results, specific_concept_sets
```

#### 3. Interactive Concept Set Builder

```python
async def interactive_concept_explorer(search_term: str):
    """Help users interactively build concept sets"""
    
    from ohdsi_webapi import WebApiClient
    
    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
    
    print(f"🔍 Exploring: '{search_term}'")
    print("=" * 40)
    
    # 1. Search for concepts
    concepts = await client.vocabulary.search(search_term)
    
    # 2. Group by domain and standard status
    domains = {}
    for concept in concepts:
        domain = concept.domain_id
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(concept)
    
    print("📋 Found concepts by domain:")
    for domain, domain_concepts in domains.items():
        standard = [c for c in domain_concepts if c.standard_concept == 'S']
        print(f"  {domain}: {len(standard)} standard concepts")
    
    # 3. Show top-level concepts (likely parents)
    condition_concepts = domains.get('Condition', [])
    standard_conditions = [c for c in condition_concepts if c.standard_concept == 'S']
    
    print(f"\n🎯 Top condition concepts for '{search_term}':")
    for i, concept in enumerate(standard_conditions[:10]):
        descendants = await client.vocabulary.descendants(concept.concept_id)
        print(f"  {i+1}. {concept.concept_name} (ID: {concept.concept_id})")
        print(f"     → Includes {len(descendants)} specific conditions")
        
        # Show a few examples
        if descendants:
            examples = descendants[:3]
            example_names = [d.concept_name for d in examples]
            print(f"     → Examples: {', '.join(example_names)}")
            if len(descendants) > 3:
                print(f"     → ...and {len(descendants) - 3} more")
        print()
    
    return standard_conditions

# Usage:
# concepts = await interactive_concept_explorer("cardiovascular disease")
# concepts = await interactive_concept_explorer("diabetes") 
# concepts = await interactive_concept_explorer("cancer")
```

#### 4. Concept Set Validation

```python
async def validate_concept_set_size(concept_id: int, source_key: str):
    """Check how many patients a concept set would include"""

    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.models.cohort import CohortDefinition
    from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

    # Create test concept set using unified models
    test_concept = Concept(
        concept_id=concept_id,
        concept_name="Test Concept",
        standard_concept="S",
        domain_id="Condition"
    )

    test_item = ConceptSetItem(
        concept=test_concept,
        include_descendants=True,
        include_mapped=False,
        is_excluded=False
    )

    test_cs = ConceptSetExpression(items=[test_item])

    # Create minimal cohort to get counts
    test_cohort = CohortDefinition(
        name="Concept Set Size Test",
        expression={"ConceptSets": [test_cs.model_dump(by_alias=True)]}  # Simplified
    )

    # Generate and get counts
    created = await client.cohortdefs.create(test_cohort)
    await client.cohortdefs.generate(created.id, source_key)
    await client.cohortdefs.poll_generation(created.id, source_key)
    counts = await client.cohortdefs.counts(created.id)

    patient_count = counts[0].subject_count if counts else 0

    # Clean up test cohort
    await client.cohortdefs.delete(created.id)

    return patient_count


async def suggest_concept_refinement(search_term: str, source_key: str):
    """Suggest concept refinements based on patient counts"""

    concepts = await interactive_concept_explorer(search_term)

    print(f"\n📊 Patient counts for different '{search_term}' definitions:")
    print("-" * 60)

    for concept in concepts[:5]:  # Test top 5 concepts
        try:
            count = await validate_concept_set_size(concept.concept_id, source_key)
            print(f"{concept.concept_name:40} → {count:,} patients")

            # Suggest based on size
            if count > 100000:
                print(f"  ⚠️  Very broad - consider more specific subtypes")
            elif count < 100:
                print(f"  ⚠️  Very narrow - consider broader category")
            else:
                print(f"  ✓  Good size for analysis")

        except Exception as e:
            print(f"{concept.concept_name:40} → Error: {e}")

        print()
```

### Best Practices for Broad Terms

1. **Always explore first** - Search and show users what concepts are available, with descendant counts
2. **Show options** - Give users both broad and specific alternatives with patient counts  
3. **Validate sizes** - Show actual patient counts for different concept definitions
4. **Document choices** - Record which concepts were included/excluded and why
5. **Iterative refinement** - Start broad, then narrow based on clinical input

This approach helps users make informed decisions about concept selection rather than blindly using overly broad or narrow definitions.

### Real Examples:

*  "Cardiovascular disease" → Could be 1 broad concept (194990) with 1,247 descendants, OR 4 specific conditions
* "Diabetes" → Type 1, Type 2, gestational, secondary diabetes all very different
* "Cancer" → Hundreds of specific cancer types with very different characteristics


#### The Solution:

Instead of guessing what the user wants, the API helps them:

- See all options with patient counts
- Compare broad vs specific approaches
- Make informed decisions about scope
- Iteratively refine their cohort definition


This is a much better approach than either:

- Defaulting to overly broad definitions (millions of patients)
- Defaulting to overly narrow definitions (dozens of patients)

The user gets to see the impact of their choices and make clinical decisions with full information
