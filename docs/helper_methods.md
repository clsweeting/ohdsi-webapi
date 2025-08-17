# Cohort Helper Methods

The OHDSI WebAPI client provides a comprehensive set of helper methods that dramatically simplify cohort building. These methods abstract away the complex JSON structures required by the OHDSI WebAPI and provide a Pythonic interface for common cohort patterns.

## What Helper Methods Replace

Without helper methods, building a cohort requires manually constructing complex nested JSON structures. Here's what a simple "males with diabetes" cohort looks like manually vs. with helpers:

### Manual Approach (Without Helpers)
```python
# Manual construction - complex and error-prone
expression = {
    "ConceptSets": [
        {
            "id": 0,
            "name": "Type 2 Diabetes",
            "expression": {
                "items": [
                    {
                        "concept": {
                            "CONCEPT_ID": 201826,
                            "CONCEPT_NAME": "Type 2 diabetes mellitus",
                            "VOCABULARY_ID": "SNOMED",
                            "DOMAIN_ID": "Condition"
                        },
                        "includeDescendants": True,
                        "includeMapped": False,
                        "isExcluded": False
                    }
                ]
            }
        }
    ],
    "PrimaryCriteria": {
        "CriteriaList": [
            {
                "ConditionOccurrence": {
                    "CodesetId": 0
                }
            }
        ],
        "ObservationWindow": {
            "PriorDays": 0,
            "PostDays": 0
        },
        "PrimaryCriteriaLimit": {
            "Type": "First"
        }
    },
    "InclusionRules": [
        {
            "name": "Male gender",
            "expression": {
                "Type": "ALL",
                "CriteriaList": [
                    {
                        "Criteria": {
                            "Person": {
                                "GenderConcept": [
                                    {
                                        "CONCEPT_ID": 8507,
                                        "CONCEPT_NAME": "MALE"
                                    }
                                ]
                            }
                        },
                        "StartWindow": {
                            "Start": {"Coeff": -1},
                            "End": {"Coeff": 1},
                            "UseIndexEnd": False,
                            "UseEventEnd": False
                        },
                        "Occurrence": {
                            "Type": 2,
                            "Count": 1
                        }
                    }
                ]
            }
        }
    ],
    "QualifiedLimit": {"Type": "First"},
    "ExpressionLimit": {"Type": "First"},
    "EndStrategy": {"Type": "DEFAULT"},
    "CensorWindow": {}
}
```

### Helper Method Approach (Clean & Simple)
```python
# Using helper methods - simple and readable
diabetes_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")
expression = client.cohorts.create_base_cohort_expression([diabetes_cs])
expression = client.cohorts.add_gender_filter(expression, "male")
```

## Core Helper Methods

### 1. Building Blocks

#### `create_concept_set(concept_id, name, include_descendants=True)`
Creates a concept set for use in cohort definitions.

**Supports both formats:**
```python
# Traditional approach
diabetes_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")

# New unified model approach
from ohdsi_cohort_schemas import Concept
concept = Concept(concept_id=201826, concept_name="Type 2 diabetes mellitus")
diabetes_cs = client.cohorts.create_concept_set(concept, "")
```

**What it replaces:** Manual construction of nested concept set JSON with proper OMOP concept structure.

#### `create_base_cohort_expression(concept_sets, primary_concept_set_id=0)`
Creates the foundation of a cohort expression with primary inclusion criteria.

**Supports both formats:**
```python
# Traditional approach
concept_sets = [diabetes_cs, hypertension_cs]
expression = client.cohorts.create_base_cohort_expression(concept_sets)

# New unified model approach  
from ohdsi_cohort_schemas import ConceptSetExpression
expr_models = [ConceptSetExpression(...), ConceptSetExpression(...)]
expression = client.cohorts.create_base_cohort_expression(expr_models)
```

**What it replaces:** Manual construction of ConceptSets, PrimaryCriteria, and base expression structure.

### 2. Demographic Filters

#### `add_gender_filter(expression, gender="male")`
Restricts cohort to specific gender.

```python
# Add male filter
male_expression = client.cohorts.add_gender_filter(expression, "male")

# Add female filter  
female_expression = client.cohorts.add_gender_filter(expression, "female")
```

**What it replaces:** Complex inclusion rule with Person criteria and gender concept mapping.

#### `add_age_filter(expression, min_age, max_age=None)`
Restricts cohort to specific age range at index date.

```python
# Adults 18-65
expression = client.cohorts.add_age_filter(expression, min_age=18, max_age=65)

# Adults 18+
expression = client.cohorts.add_age_filter(expression, min_age=18)
```

**What it replaces:** Complex age calculation criteria with date arithmetic and observation period logic.

### 3. Temporal Filters

#### `add_time_window_filter(expression, concept_set_id, days_before, days_after)`
Requires events within a specific time window around index date.

```python
# Must have hypertension 30 days before to 7 days after diabetes
expression = client.cohorts.add_time_window_filter(
    expression, 
    concept_set_id=1,  # hypertension concept set
    days_before=30, 
    days_after=7
)
```

**What it replaces:** Complex temporal criteria with start/end windows and date calculations.

#### `add_observation_period_filter(expression, days_before=365, days_after=0)`
Requires minimum observation period before/after index date.

```python
# Must have 1 year of observation before index
expression = client.cohorts.add_observation_period_filter(expression, days_before=365)
```

**What it replaces:** Observation period criteria with complex date arithmetic.

#### `add_prior_observation_filter(expression, min_days=365)`
Requires minimum continuous observation before index date.

```python
# Must have 2 years of prior observation
expression = client.cohorts.add_prior_observation_filter(expression, min_days=730)
```

**What it replaces:** Prior observation criteria with enrollment period calculations.

### 4. Clinical Event Filters

#### `add_visit_filter(expression, visit_concept_ids, occurrence_count=1)`
Requires specific types of healthcare visits.

```python
# Must have inpatient visit
inpatient_visit_id = 9201  # OMOP concept for inpatient visit
expression = client.cohorts.add_visit_filter(expression, [inpatient_visit_id])
```

**What it replaces:** Visit occurrence criteria with concept set mapping and occurrence counting.

#### `add_measurement_filter(expression, concept_set_id, value_min=None, value_max=None, unit_concept_id=None)`
Requires laboratory values or measurements within specific ranges.

```python
# HbA1c > 7.0%
hba1c_cs_id = 2  # Concept set for HbA1c
expression = client.cohorts.add_measurement_filter(
    expression, 
    concept_set_id=hba1c_cs_id,
    value_min=7.0,
    unit_concept_id=8554  # Percentage unit
)
```

**What it replaces:** Complex measurement criteria with value ranges, units, and temporal logic.

#### `add_drug_era_filter(expression, concept_set_id, min_days=30, gap_days=30)`
Requires drug exposure periods (drug eras) of minimum duration.

```python
# Must have 90+ days of metformin exposure
metformin_cs_id = 3
expression = client.cohorts.add_drug_era_filter(
    expression,
    concept_set_id=metformin_cs_id,
    min_days=90
)
```

**What it replaces:** Drug era criteria with gap calculations and duration requirements.

#### `add_multiple_conditions_filter(expression, concept_set_ids, occurrence_type="any")`
Requires multiple conditions (comorbidities).

```python
# Must have both diabetes AND hypertension
expression = client.cohorts.add_multiple_conditions_filter(
    expression,
    concept_set_ids=[0, 1],  # diabetes and hypertension
    occurrence_type="all"
)
```

**What it replaces:** Complex multiple condition criteria with AND/OR logic.

### 5. Exclusion Criteria

#### `add_exclusion_condition(expression, concept_set_id, days_before=0, days_after=0)`
Excludes patients with specific conditions.

```python
# Exclude patients with Type 1 diabetes
type1_diabetes_cs_id = 4
expression = client.cohorts.add_exclusion_condition(
    expression,
    concept_set_id=type1_diabetes_cs_id
)
```

#### `add_exclusion_drug(expression, concept_set_id, days_before=365, days_after=0)`
Excludes patients with specific drug exposures.

```python
# Exclude patients with insulin in past year
insulin_cs_id = 5
expression = client.cohorts.add_exclusion_drug(
    expression,
    concept_set_id=insulin_cs_id,
    days_before=365
)
```

#### `add_exclusion_procedure(expression, concept_set_id, days_before=365, days_after=0)`
Excludes patients with specific procedures.

```python
# Exclude patients with recent surgery
surgery_cs_id = 6
expression = client.cohorts.add_exclusion_procedure(
    expression,
    concept_set_id=surgery_cs_id,
    days_before=90
)
```

#### `add_exclusion_death(expression, days_after_index=30)`
Excludes patients who die within specified period after index.

```python
# Exclude patients who die within 30 days
expression = client.cohorts.add_exclusion_death(expression, days_after_index=30)
```

**What exclusions replace:** Complex exclusion criteria with temporal windows and event type mapping.

### 6. Advanced Building

#### `build_incremental_cohort(source_key, name, base_criteria, filters=[], exclusions=[])`
Builds and tests cohorts incrementally, applying filters one by one.

```python
# Build cohort step by step with intermediate counts
result = await client.cohorts.build_incremental_cohort(
    source_key="CDM",
    name="Complex Diabetes Cohort",
    base_criteria=[diabetes_cs],
    filters=[
        {"type": "gender", "gender": "male"},
        {"type": "age", "min_age": 18, "max_age": 65},
        {"type": "prior_observation", "min_days": 365}
    ],
    exclusions=[
        {"type": "condition", "concept_set_id": type1_diabetes_cs_id}
    ]
)

print(f"Final cohort size: {result['final_count']}")
for step in result['steps']:
    print(f"After {step['filter']}: {step['count']} patients")
```

**What it replaces:** Manual iteration through filter combinations with individual cohort generation and counting.

## Complete Example: Complex Cohort

Here's a complete example showing how helper methods simplify building a complex cohort:

```python
from ohdsi_webapi import WebApiClient
from ohdsi_webapi.models.cohort import CohortDefinition

client = WebApiClient("https://your-webapi-url/WebAPI")

# 1. Create concept sets
diabetes_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")
hypertension_cs = client.cohorts.create_concept_set(316866, "Hypertension")  
metformin_cs = client.cohorts.create_concept_set(1503297, "Metformin")

# 2. Build base expression
expression = client.cohorts.create_base_cohort_expression([
    diabetes_cs, 
    hypertension_cs, 
    metformin_cs
])

# 3. Add inclusion filters
expression = client.cohorts.add_gender_filter(expression, "male")
expression = client.cohorts.add_age_filter(expression, min_age=18, max_age=65)
expression = client.cohorts.add_prior_observation_filter(expression, min_days=365)
expression = client.cohorts.add_multiple_conditions_filter(expression, [0, 1], "all")  # diabetes AND hypertension
expression = client.cohorts.add_drug_era_filter(expression, 2, min_days=90)  # 90+ days metformin

# 4. Add exclusions  
type1_diabetes_cs = client.cohorts.create_concept_set(201254, "Type 1 Diabetes")
expression = client.cohorts.add_exclusion_condition(expression, 3)  # exclude T1DM
expression = client.cohorts.add_exclusion_death(expression, days_after_index=30)

# 5. Create cohort
cohort = CohortDefinition(
    name="Male T2DM + HTN on Metformin",
    description="Males 18-65 with T2DM and hypertension on metformin therapy",
    expression=expression
)

saved_cohort = client.cohorts.create(cohort)
print(f"Created cohort {saved_cohort.id}: {saved_cohort.name}")
```

## Backward Compatibility

All helper methods support both traditional dictionaries and new unified models:

```python
# Works with dicts (traditional)
expression_dict = client.cohorts.create_base_cohort_expression([diabetes_cs])
filtered_dict = client.cohorts.add_gender_filter(expression_dict, "male")

# Works with unified models (new)
from ohdsi_cohort_schemas import CohortExpression, ConceptSetExpression
expr_model = CohortExpression(...)
filtered_model = client.cohorts.add_gender_filter(expr_model, "male")  # Returns dict
```

## Benefits of Helper Methods

1. **Readability**: Code clearly expresses clinical intent
2. **Maintainability**: Changes to OHDSI JSON format are isolated to helper methods  
3. **Correctness**: Reduces errors from manual JSON construction
4. **Productivity**: Builds complex cohorts in minutes instead of hours
5. **Clinical Focus**: Researchers focus on logic, not JSON structure
6. **Type Safety**: When used with unified models, provides compile-time validation

## Migration Guide

If you have existing manual JSON construction:

1. **Identify patterns**: Look for repeated JSON structures
2. **Replace with helpers**: Use appropriate helper methods
3. **Test equivalence**: Verify cohorts produce same results
4. **Simplify gradually**: Migrate one filter at a time

The helper methods represent years of OHDSI cohort building experience distilled into a simple, powerful API that makes cohort research accessible to clinical researchers without deep JSON expertise.
