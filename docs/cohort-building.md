# Cohort Building with OHDSI WebAPI

This guide explains how to create cohorts programmatically using the OHDSI WebAPI, including incremental filtering and getting counts at each step.

## Overview

OHDSI cohorts are defined using a JSON expression that specifies:
1. **Initial Events** - What qualifies someone for entry into the cohort
2. **Inclusion & Exclusion Criteria** - Additional rules that must be met
3. **Cohort Exit** - When someone leaves the cohort
4. **Censoring** - Rules for observation period requirements

## Basic Cohort Structure

A cohort definition consists of:
- **ConceptSets**: Reusable groups of medical concepts
- **PrimaryCriteria**: Initial qualifying events
- **InclusionRules**: Additional filtering criteria
- **EndStrategy**: How/when the cohort period ends
- **CensoringCriteria**: Observation period requirements

## Example: Males over 40 with Diabetes

Here's how you'd build a cohort for "males over 40 who have had diabetes in the last 2 years":

```python
from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

# 1. Define concept sets for diabetes using the unified models
diabetes_concept = Concept(
    concept_id=201826,
    concept_name="Type 2 diabetes mellitus",
    standard_concept="S",
    concept_code="44054006",
    concept_class_id="Clinical Finding",
    vocabulary_id="SNOMED",
    domain_id="Condition"
)

diabetes_concept_item = ConceptSetItem(
    concept=diabetes_concept,
    include_descendants=True,
    include_mapped=False,
    is_excluded=False
)

diabetes_concept_expression = ConceptSetExpression(
    items=[diabetes_concept_item]
)

# Convert to WebAPI format when needed
diabetes_concepts = {
    "id": 0,
    "name": "Type 2 Diabetes",
    "expression": diabetes_concept_expression.model_dump(by_alias=True)
}

# 2. Build the cohort definition
cohort_expression = {
    "conceptSets": [diabetes_concepts],
    "primaryCriteria": {
        "criteriaList": [
            {
                "conditionOccurrence": {
                    "conceptSetId": 0,  # References diabetes concept set
                    "conditionType": [
                        {
                            "conceptId": 32020,  # EHR Chief Complaint
                            "conceptName": "EHR Chief Complaint"
                        }
                    ]
                }
            }
        ],
        "observationWindow": {
            "priorDays": 0,
            "postDays": 0
        },
        "primaryLimit": {
            "type": "First"
        }
    },
    "inclusionRules": [
        {
            "name": "Male gender",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {
                            "person": {
                                "genderConcept": [
                                    {
                                        "conceptId": 8507,  # Male
                                        "conceptName": "MALE"
                                    }
                                ]
                            }
                        },
                        "startWindow": {
                            "start": {
                                "coeff": -1
                            },
                            "end": {
                                "coeff": 1
                            },
                            "useIndexEnd": false,
                            "useEventEnd": false
                        },
                        "occurrence": {
                            "type": 2,
                            "count": 1
                        }
                    }
                ]
            }
        },
        {
            "name": "Age >= 40",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {
                            "person": {
                                "ageAtStart": {
                                    "value": 40,
                                    "op": "gte"
                                }
                            }
                        },
                        "startWindow": {
                            "start": {
                                "coeff": -1
                            },
                            "end": {
                                "coeff": 1
                            },
                            "useIndexEnd": false,
                            "useEventEnd": false
                        },
                        "occurrence": {
                            "type": 2,
                            "count": 1
                        }
                    }
                ]
            }
        },
        {
            "name": "Diabetes in last 2 years",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {
                            "conditionOccurrence": {
                                "conceptSetId": 0
                            }
                        },
                        "startWindow": {
                            "start": {
                                "coeff": -730,  # 2 years before
                                "dateField": "StartDate"
                            },
                            "end": {
                                "coeff": 0,
                                "dateField": "StartDate"
                            },
                            "useIndexEnd": false,
                            "useEventEnd": false
                        },
                        "occurrence": {
                            "type": 2,
                            "count": 1
                        }
                    }
                ]
            }
        }
    ],
    "endStrategy": {
        "type": "CUSTOM_ERA",
        "gapDays": 0,
        "offset": 0
    },
    "censoringCriteria": []
}
```
## Key Concepts

### Concept Sets
- Reusable groups of medical concepts (conditions, drugs, procedures)
- Can include descendant concepts (e.g., all types of diabetes)
- Reference OMOP standardized vocabularies

### Primary Criteria
- Defines the "index event" that qualifies someone for the cohort
- Usually a condition, drug exposure, procedure, etc.
- Sets the "index date" for each person

### Inclusion Rules
- Additional criteria that must be met
- Applied as filters after the primary criteria
- Can reference demographics, time windows, concept occurrences

### Time Windows
- Relative to the index date
- Negative coefficients = before index date
- Positive coefficients = after index date
- Used for "in the last X years" type criteria

## Common Patterns

### Demographics
```python
# Male gender
"person": {
    "genderConcept": [{"conceptId": 8507}]  # 8532 for Female
}

# Age at index date
"person": {
    "ageAtStart": {"value": 40, "op": "gte"}  # >= 40 years old
}
```

### Time-based Conditions
```python
# Condition in last 2 years before index
"startWindow": {
    "start": {"coeff": -730},  # 2 years before
    "end": {"coeff": 0}        # index date
}
```

### Multiple Conditions
```python
# Must have BOTH condition A AND condition B
"type": "ALL",
"criteriaList": [condition_a_criteria, condition_b_criteria]

# Must have EITHER condition A OR condition B  
"type": "ANY",
"criteriaList": [condition_a_criteria, condition_b_criteria]
```

This approach gives you fine-grained control over cohort building and lets you see exactly how each filter affects your population size.

## Simple Example: Quick Incremental Cohort Building

For most use cases, you can use our simplified helper methods instead of building the complex JSON structures manually:

```python
from ohdsi_webapi import WebApiClient


async def example_incremental_cohort():
    """Example: Males over 40 with diabetes in last 2 years"""

    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

    # Get your data source
    sources = client.source.sources()
    source_key = sources[0].source_key  # Use first available source

    # Define what we're looking for using the unified models
    from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

    diabetes_concept = Concept(
        concept_id=201826,
        concept_name="Type 2 diabetes mellitus",
        standard_concept="S",
        concept_code="44054006",
        concept_class_id="Clinical Finding",
        vocabulary_id="SNOMED",
        domain_id="Condition"
    )

    diabetes_item = ConceptSetItem(
        concept=diabetes_concept,
        include_descendants=True,
        include_mapped=False,
        is_excluded=False
    )

    diabetes_cs = ConceptSetExpression(items=[diabetes_item])

    # Define filters to apply incrementally
    filters = [
        {"type": "gender", "gender": "male", "name": "Male"},
        {"type": "age", "min_age": 40, "name": "Age 40+"},
        {"type": "time_window", "concept_set_id": 0, "days_before": 730,
         "filter_name": "Diabetes in last 2 years"}
    ]

    # Build cohort step by step - this does all the work!
    results = await client.cohortdefs.build_incremental_cohort(
        source_key=source_key,
        base_name="Diabetes Study",
        concept_sets=[diabetes_cs],
        filters=filters
    )

    # See counts at each step
    print("📊 Cohort Building Results:")
    for i, (cohort, count) in enumerate(results):
        print(f"Step {i + 1}: {count:,} patients - {cohort.name}")

        if i > 0:
            prev_count = results[i - 1][1]
            reduction = prev_count - count
            pct_reduction = (reduction / prev_count * 100) if prev_count > 0 else 0
            print(f"  Reduction: -{reduction:,} patients (-{pct_reduction:.1f}%)")

    return results[-1][0]  # Return final cohort

# Example output:
# Step 1: 45,230 patients - All diabetes patients
# Step 2: 23,115 patients - Male diabetes patients
#   Reduction: -22,115 patients (-48.9%)
# Step 3: 18,492 patients - Male diabetes patients 40+  
#   Reduction: -4,623 patients (-20.0%)
# Step 4: 12,847 patients - Male diabetes patients 40+ (last 2 years)
#   Reduction: -5,645 patients (-30.5%)
```

This gives you exactly what you need:
- **Incremental filtering** with counts at each step
- **Clear impact** of each filter on population size  
- **Automated cohort creation** without complex JSON structures
- **Real patient counts** from your actual data source

Much simpler than building the JSON expressions manually!

## Exclusion Criteria

In addition to inclusion criteria, ATLAS cohorts support **exclusion criteria** to remove patients who meet certain conditions. This is essential for creating clinically relevant cohorts.

### Common Exclusion Use Cases

1. **Cancer History** - Exclude patients with cancer for cardiac studies
2. **Pregnancy** - Exclude pregnant women from certain studies  
3. **Recent Procedures** - Exclude patients with recent surgeries
4. **Contraindicated Medications** - Exclude patients on specific drugs
5. **Early Death** - Exclude patients who died shortly after index date

### Adding Exclusion Criteria

```python
# Base cohort for heart failure patients
heart_failure_cs = client.cohortdefs.create_concept_set(444094, "Heart Failure")
cancer_cs = client.cohortdefs.create_concept_set(443392, "Cancer", include_descendants=True)

concept_sets = [heart_failure_cs, cancer_cs]
base_expression = client.cohortdefs.create_base_cohort_expression(concept_sets)

# Add exclusion: No cancer in last 5 years
excluded_expression = client.cohortdefs.add_exclusion_condition(
    base_expression,
    concept_set_id=1,  # Cancer concept set
    days_before=1825,  # 5 years before index
    exclusion_name="No cancer history (5 years)"
)

# Add exclusion: No chemotherapy in last year  
final_expression = client.cohortdefs.add_exclusion_drug(
    excluded_expression,
    concept_set_id=2,  # Chemotherapy drugs
    days_before=365,  # 1 year
    exclusion_name="No recent chemotherapy"
)
```

### Types of Exclusions

#### 1. Condition Exclusions

```python
# Exclude patients with specific medical conditions
expression = client.cohortdefs.add_exclusion_condition(
    expression,
    concept_set_id=1,
    days_before=365,  # Look back 1 year
    exclusion_name="No cancer history"
)
```

#### 2. Drug Exclusions

```python
# Exclude patients taking certain medications
expression = client.cohortdefs.add_exclusion_drug(
    expression,
    concept_set_id=2,
    days_before=90,  # Look back 90 days
    exclusion_name="No contraindicated meds"
)
```

#### 3. Procedure Exclusions

```python
# Exclude patients with recent procedures
expression = client.cohortdefs.add_exclusion_procedure(
    expression,
    concept_set_id=3,
    days_before=180,  # Look back 6 months
    exclusion_name="No recent surgery"
)
```

#### 4. Death Exclusions

```python
# Exclude patients who died early (for outcome studies)
expression = client.cohortdefs.add_exclusion_death(
    expression,
    days_after_index=30  # Must survive 30 days
)
```

### Complete Example with Inclusions + Exclusions

```python
async def heart_failure_study_cohort():
    """Real-world example: Heart failure study with comprehensive criteria"""

    from ohdsi_webapi import WebApiClient
    from ohdsi_cohort_schemas import ConceptSetExpression, ConceptSetItem, Concept

    client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

    # Define concept sets using unified models
    def create_concept_set(concept_id: int, name: str, include_descendants: bool = True):
        # Note: In real usage, you'd fetch the full concept details
        concept = Concept(
            concept_id=concept_id,
            concept_name=name,
            standard_concept="S",
            domain_id="Condition"  # Simplified for example
        )

        item = ConceptSetItem(
            concept=concept,
            include_descendants=include_descendants,
            include_mapped=False,
            is_excluded=False
        )

        return ConceptSetExpression(items=[item])

    # Create all needed concept sets
    heart_failure_cs = create_concept_set(444094, "Heart Failure")
    cancer_cs = create_concept_set(443392, "Cancer", True)
    chemotherapy_cs = create_concept_set(21601782, "Chemotherapy", True)
    cardiac_surgery_cs = create_concept_set(4336464, "Cardiac Surgery", True)

    concept_sets = [heart_failure_cs, cancer_cs, chemotherapy_cs, cardiac_surgery_cs]

    # Define inclusion criteria (what we want)
    inclusion_filters = [
        {"type": "gender", "gender": "male", "name": "Male patients"},
        {"type": "age", "min_age": 18, "max_age": 80, "name": "Age 18-80"},
        {"type": "time_window", "concept_set_id": 0, "days_before": 365,
         "filter_name": "Heart failure in last year"}
    ]

    # Define exclusion criteria (what we don't want)
    exclusions = [
        {
            "type": "condition",
            "concept_set_id": 1,  # Cancer
            "days_before": 1825,  # 5 years
            "name": "No cancer history (5 years)"
        },
        {
            "type": "drug",
            "concept_set_id": 2,  # Chemotherapy  
            "days_before": 365,  # 1 year
            "name": "No chemotherapy (1 year)"
        },
        {
            "type": "procedure",
            "concept_set_id": 3,  # Cardiac surgery
            "days_before": 180,  # 6 months
            "name": "No recent cardiac surgery"
        },
        {
            "type": "death",
            "days_after_index": 30,
            "name": "Survived at least 30 days"
        }
    ]

    # Build cohort with both inclusions and exclusions
    results = await client.cohortdefs.build_incremental_cohort(
        source_key="your_source",
        base_name="Heart Failure Study",
        concept_sets=concept_sets,
        filters=inclusion_filters,
        exclusions=exclusions  # New parameter!
    )

    # Show results
    for i, (cohort, count) in enumerate(results):
        step_name = cohort.name.split(" - ")[-1]
        print(f"Step {i + 1}: {count:,} patients - {step_name}")

        if i > 0:
            prev_count = results[i - 1][1]
            if "Exclude" in step_name:
                excluded = prev_count - count
                print(f"  → {excluded:,} patients excluded")
            else:
                filtered = prev_count - count
                print(f"  → {filtered:,} patients filtered")

    return results[-1][0]  # Final cohort

# Example output:
# Step 1: 45,230 patients - Base criteria
# Step 2: 23,115 patients - Male patients
#   → 22,115 patients filtered
# Step 3: 18,492 patients - Age 18-80
#   → 4,623 patients filtered  
# Step 4: 12,847 patients - Heart failure in last year
#   → 5,645 patients filtered
# Step 5: 11,203 patients - Exclude No cancer history (5 years)
#   → 1,644 patients excluded
# Step 6: 10,887 patients - Exclude No chemotherapy (1 year)  
#   → 316 patients excluded
# Step 7: 10,156 patients - Exclude No recent cardiac surgery
#   → 731 patients excluded
# Step 8: 9,834 patients - Exclude Survived at least 30 days
#   → 322 patients excluded
```

### Exclusion vs Inclusion Logic

**Inclusion Rules** (AND logic):
- Patient MUST meet all inclusion criteria
- Used for: Demographics, required conditions, time windows

**Exclusion Criteria** (NOT logic):  
- Patient must NOT have any exclusion conditions
- Used for: Contraindications, competing conditions, early outcomes

### Best Practices for Exclusions

1. **Apply exclusions last** - Include first, then exclude to see the impact
2. **Use appropriate time windows** - Cancer history = 5 years, recent surgery = 6 months
3. **Document clinical rationale** - Why are you excluding each condition?
4. **Consider competing risks** - Death exclusions for outcome studies
5. **Test sensitivity** - Try different exclusion windows to see impact
6. **Balance precision vs power** - Too many exclusions = small cohorts

This approach gives you the full power of ATLAS cohort definitions - precisely defining both who you want (inclusions) and who you don't want (exclusions) in your study population.
