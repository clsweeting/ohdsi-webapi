# Example of creating a Cohort using the OHDSI WebAPI Client 

We are going to go through the process of creating a cohort for "Type 2 diabetes males under the age of 40", assuming that the user doesn't actually know much about OMOP data. 

## 1. Initial Discovery 

### Create a WebAPI Client:

```python
from ohdsi_webapi import WebApiClient

base_url = "https://atlas-demo.ohdsi.org/WebAPI"
client = WebApiClient(base_url)
```

### Check which domains are available: 

```python
domains = client.vocabulary.domains()
print("Available domains:")
for domain in domains:
    print(f"  - {domain}")
```

which may return something like this: 

> Available domains:
>  - {'domainId': 'Condition', 'domainName': 'Condition'}
>  - {'domainId': 'Condition/Device', 'domainName': 'Condition/Device'}
>  - {'domainId': 'Condition/Drug', 'domainName': 'Condition/Drug'}
>  - {'domainId': 'Condition/Meas', 'domainName': 'Condition/Measurement'}
>  - {'domainId': 'Condition/Obs', 'domainName': 'Condition/Observation'}
>  - {'domainId': 'Condition/Procedure', 'domainName': 'Condition/Procedure'}
>  - {'domainId': 'Cost', 'domainName': 'Cost'}
>  - {'domainId': 'Currency', 'domainName': 'Currency'}
>  - {'domainId': 'Device', 'domainName': 'Device'}
>  - {'domainId': 'Device/Drug', 'domainName': 'Device/
> - ... etc. 

### Check which vocabularies are available: 

```python 
vocabularies = client.vocabulary.vocabularies()
print(f"\nFound {len(vocabularies)} vocabularies:")
for vocab in vocabularies: 
    vocab_id = vocab.vocabulary_id if hasattr(vocab, 'vocabulary_id') else vocab.get('vocabularyId', str(vocab))
    vocab_name = vocab.vocabulary_name if hasattr(vocab, 'vocabulary_name') else vocab.get('vocabularyName', '')
    print(f"  - {vocab_id}: {vocab_name}")
```

This may return something like this: 

> Found 91 vocabularies:
>  - APC: Ambulatory Payment Classification (CMS)
>  - EphMRA ATC: Anatomical Classification of Pharmaceutical Products (EphMRA)
>  - CVX: CDC Vaccine Administered CVX (NCIRD)
>  - US Census: Census regions of the United States (USCB)
>  - Multum: Cerner Multum (Cerner)
>  - CPT4: Current Procedural Terminology version 4 (AMA)
>  - NAACCR: Data Standards & Data Dictionary Volume II (NAACCR)
>  - DRG: Diagnosis-related group (CMS)
>  - Cancer Modifier: Diagnostic Modifiers of Cancer (OMOP)
>  - ICD10PCS: ICD-10 Procedure Coding System (CMS)
>  - ICDO3: International Classification of Diseases for Oncology, Third Edition (WHO)
>  - ICD10CM: International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS)
>  - ICD10: International Classification of Diseases, Tenth Revision (WHO)
 > - ..... etc


## 2. Search for the Concept describing 'Type 2 Diabetes'

We could just do this: 

```python 
diabetes_concepts = client.vocabulary.search("type 2 diabetes", page_size=1000)
```

But that is a very wide search and will return hundreds of results (525 at the time of writing).  

We can narrow the search by also specifying the **domain** ('Condition', which we know is a valid domain from the first step above) and the **vocabulary**. 
  
```python
# Search for type 2 diabetes in SNOMED vocabulary, Condition domain
snomed_results = client.vocabulary.search(
    query="type 2 diabetes",
    domain_id="Condition",
    vocabulary_id="SNOMED", 
    standard_concept="S"
)
```

How did we know to specify 'SNOMED' ? It's the usual suspect for conditions - see [this guide to understand how to choose the right vocabulary](./example-choosing-the-right-vocabulary.md).

Unfamiliar with `standard_concept` attribute ? See [standard concepts](./example-standard-concepts.md) for more information.

This search still returns 107 results at the time of writing: 

> SNOMED results: 107
>   - ID: 4321756, Name: Acanthosis nigricans due to type 2 diabetes mellitus
>   - ID: 36717156, Name: Acidosis due to type 2 diabetes mellitus
>   - ID: 43531588, Name: Angina associated with type 2 diabetes mellitus
>   - ID: 45769888, Name: Ankle ulcer due to type 2 diabetes mellitus
> - ... etc. 

## 3. Identify the specific concept 

As you can see from some of the search results, many of the matches are not the actual condition but mention 'due to', 'with' or 'associated'.  In medical terms: 

- "due to" --> Complications or Secondary conditions
- "with" --> Comorbidities or Associated conditions
- "associated" --> Comorbidities or Related conditions


An LLM would make fast work of identifying the specific base concept ("type 2 diabetes"). 

But you could improve your odds programmatically too: 

```python 
# Ignore 
for concept in snomed_results:
    name = concept.concept_name.lower()
    if "due to" not in name and "with" not in name and "associated" not in name:
        print(f"ID: {concept.concept_id}, Name: {concept.concept_name}")
```

This returns a much more manageable 9 results: 

> - ID: 4130162, Name: Insulin treated type 2 diabetes mellitus
> - ID: 4063043, Name: Pre-existing type 2 diabetes mellitus
> - ID: 43531010, Name: Pre-existing type 2 diabetes mellitus in pregnancy
> - ID: 4129519, Name: Pregnancy and type 2 diabetes mellitus
> - ID: 201826, Name: Type 2 diabetes mellitus
> - ID: 45757508, Name: Type 2 diabetes mellitus controlled by diet
> - ID: 4230254, Name: Type 2 diabetes mellitus in nonobese
> - ID: 4304377, Name: Type 2 diabetes mellitus in obese
> - ID: 40485020, Name: Well controlled type 2 diabetes mellitus

From which we can see that ID 201826 ("Type 2 diabetes mellitus") is the base condition. 


## 4. Create a Concept Set 

We now need to create a concept set that includes Type 2 diabetes and potentially its descendants.

For this, we'll use the structured models from the `ohdsi-cohort-schemas` library for building the concept set expression:

```python 
from ohdsi_cohort_schemas import (
    Concept,
    ConceptSetItem, 
    ConceptSetExpression
)

# Create the Type 2 diabetes concept using the schema model
diabetes_concept = Concept(
    concept_id=201826,
    concept_name="Type 2 diabetes mellitus",
    standard_concept="S",
    concept_code="44054006",
    concept_class_id="Clinical Finding",
    vocabulary_id="SNOMED",
    domain_id="Condition"
)

# Create a concept set item using the schema model
diabetes_conceptset_item = ConceptSetItem(
    concept=diabetes_concept,
    include_descendants=True,  # Include descendant concepts
    include_mapped=False,      # Don't include mapped concepts
    is_excluded=False          # Include this concept (don't exclude)
)

# Create the concept set expression
concept_set_expression = ConceptSetExpression(
    items=[diabetes_conceptset_item]
)

# Create the concept set via WebAPI
saved_concept_set = client.concept_sets.create(
    name="Type 2 Diabetes Mellitus",
    expression=concept_set_expression.model_dump(by_alias=True)
)

print(f"Created concept set with ID: {saved_concept_set.id}")
```


## 5. Add Inclusion Criteria 

If you wish to then filter by males who are under 40, you COULD do this if you really love writing and reading JSON:  

```python 

from ohdsi_webapi.models.cohort import CohortDefinition

# Build the complete cohort definition
cohort_definition_json = {
    "ConceptSets": [
        {
            "id": 0,  # Reference ID for this concept set within the cohort
            "name": "Type 2 Diabetes Mellitus",
            "expression": {
                "items": [
                    {
                        "concept": {"CONCEPT_ID": 201826},
                        "isExcluded": False,
                        "includeDescendants": True,
                        "includeMapped": False
                    }
                ]
            }
        }
    ],
    "PrimaryCriteria": {
        "CriteriaList": [
            {
                "ConditionOccurrence": {
                    "ConceptSetId": 0,  # References concept set ID 0 above
                    "ConditionTypeExclude": False
                }
            }
        ],
        "ObservationWindow": {
            "PriorDays": 0,
            "PostDays": 0
        },
        "PrimaryCriteriaLimit": {
            "Type": "First"  # First occurrence of diabetes
        }
    },
    "InclusionRules": [
        {
            "name": "Male patients",
            "expression": {
                "Type": "ALL",
                "CriteriaList": [
                    {
                        "Criteria": {
                            "Demographics": {
                                "Gender": [{"CONCEPT_ID": 8507}]  # Male concept ID
                            }
                        },
                        "StartWindow": {
                            "Start": {"Coeff": 0},
                            "End": {"Coeff": 0},
                            "UseIndexEnd": False,
                            "UseEventEnd": False
                        },
                        "RestrictVisit": False,
                        "IgnoreObservationPeriod": False,
                        "Occurrence": {
                            "Type": 2,
                            "Count": 1
                        }
                    }
                ]
            }
        },
        {
            "name": "Age under 40 at diagnosis",
            "expression": {
                "Type": "ALL",
                "CriteriaList": [
                    {
                        "Criteria": {
                            "Demographics": {
                                "AgeAtStart": {"Value": 40, "Op": "lt"}  # Less than 40
                            }
                        },
                        "StartWindow": {
                            "Start": {"Coeff": 0},
                            "End": {"Coeff": 0},
                            "UseIndexEnd": False,
                            "UseEventEnd": False
                        },
                        "RestrictVisit": False,
                        "IgnoreObservationPeriod": False,
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
    "CollapseSettings": {
        "CollapseType": "ERA",
        "EraPad": 0
    },
    "CensoringCriteria": [],
    "cdmVersionRange": ">=5.0.0"
}

# Create the cohort definition
cohort_def = CohortDefinition(
    name="Type 2 Diabetes Males Under 40",
    description="Male patients diagnosed with type 2 diabetes mellitus who are under 40 years old at diagnosis",
    expressionType="SIMPLE_EXPRESSION",
    expression=cohort_definition_json
)
```

... but yeah, who's going to create that JSON without an LLM ? 

Fortunately, we have the [OHDSI Cohort Schemas](https://github.com/clsweeting/ohdsi-cohort-schemas) library to help. 


## 6. Create Inclusion rule for 'male'

Reminder - we wish to filter this by gender (males) and age (under 40). 

First we need to find the Concept for Male from the 'Gender' vocabulary and 'Gender' domain.

```python 
# Search for male gender concept
male_concepts = client.vocabulary.search(
    query='male',
    domain_id='Gender',
    vocabulary_id='Gender',
    standard_concept='S'
)

for concept in male_concepts: 
    print(f"  - ID: {concept.concept_id}, Name: {concept.concept_name}, Code: {concept.concept_code}")
```

Which outputs just two matches: 

> - ID: 8532, Name: FEMALE, Code: F
> - ID: 8507, Name: MALE, Code: M

So we can create a male inclusion rule using the cohort schema models:

```python
from ohdsi_cohort_schemas import Concept
from ohdsi_cohort_schemas.models.cohort import InclusionRule
from ohdsi_cohort_schemas.models.criteria import DemographicCriteria, CorrelatedCriteria

# Create the male concept
male_concept = Concept(
    concept_id=8507,
    concept_name="MALE",
    standard_concept="S", 
    concept_code="M",
    vocabulary_id="Gender",
    domain_id="Gender"
)

# Create inclusion rule for males
male_inclusion_rule = InclusionRule(
    name="Male patients",
    description="Include only male patients",
    expression=CorrelatedCriteria(
        type="ALL",
        criteria_list=[],
        demographic_criteria_list=[
            DemographicCriteria(
                gender=[male_concept]
            )
        ],
        groups=[]
    )
)
```

## 7. Create inclusion rule for age 

```python 
from ohdsi_cohort_schemas.models.criteria import AgeRange

# Create inclusion rule for patients under 40
age_inclusion_rule = InclusionRule(
    name="Age under 40 at diagnosis",
    description="Patients must be under 40 years old at the time of diabetes diagnosis",
    expression=CorrelatedCriteria(
        type="ALL",
        criteria_list=[],
        demographic_criteria_list=[
            DemographicCriteria(
                age=AgeRange(
                    value=40,
                    op="lt"  # Less than 40
                )
            )
        ],
        groups=[]
    )
)
```

Note: The cohort schema models use the same field names and structure as the WebAPI JSON, but with proper Python types and validation. 


## 8. Put it all together 

```python 
from ohdsi_cohort_schemas import (
    CohortExpression,
    ConceptSet, 
    ConceptSetExpression,
    ConceptSetItem,
    Concept,
    Limit
)
from ohdsi_cohort_schemas.models.cohort import (
    InclusionRule, 
    PrimaryCriteria
)
from ohdsi_cohort_schemas.models.criteria import (
    DemographicCriteria, 
    ConditionOccurrence,
    CorrelatedCriteria,
    AgeRange
)
from ohdsi_cohort_schemas.models.common import ObservationWindow

# Create the Type 2 diabetes concept
diabetes_concept = Concept(
    concept_id=201826,
    concept_name="Type 2 diabetes mellitus", 
    standard_concept="S",
    concept_code="44054006",
    concept_class_id="Clinical Finding",
    vocabulary_id="SNOMED",
    domain_id="Condition"
)

# Create concept set item
diabetes_conceptset_item = ConceptSetItem(
    concept=diabetes_concept,
    include_descendants=True,
    include_mapped=False, 
    is_excluded=False
)

# Create concept set
diabetes_concept_set = ConceptSet(
    id=0,
    name="Type 2 Diabetes Mellitus",
    expression=ConceptSetExpression(items=[diabetes_conceptset_item])
)

# Create primary criteria - this defines what makes someone eligible for the cohort
primary_criteria = PrimaryCriteria(
    criteria_list=[],  # Will be populated with condition occurrence
    observation_window=ObservationWindow(
        prior_days=0, 
        post_days=0
    ),
    primary_criteria_limit=Limit(type="First")
)

# Build the cohort expression using proper models
cohort_expression = CohortExpression(
    concept_sets=[diabetes_concept_set],
    primary_criteria=primary_criteria,
    inclusion_rules=[male_inclusion_rule, age_inclusion_rule],
    censoring_criteria=[]
)

# Convert to dictionary for WebAPI - note the use of by_alias to get proper field names
cohort_dict = cohort_expression.model_dump(by_alias=True, exclude_none=True) 
```

### Validate the cohort_dict (optional): 

```python 
# Try to validate the cohort expression using the schemas
from ohdsi_cohort_schemas import validate_webapi_schema_only

try:
    validated_cohort = validate_webapi_schema_only(cohort_dict)
    print("✅ Cohort expression validates successfully")
except Exception as e:
    print(f"❌ Validation error: {e}")
```


### Create the cohort using WebAPI client

```python 
from ohdsi_webapi.models.cohort import CohortDefinition
from datetime import datetime

# Use timestamp to prevent duplicate names and avoid 409 Conflict errors
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
cohort_name = f"Type 2 Diabetes Males Under 40 - {timestamp}"

# Create the cohort definition - the validator now handles both CohortExpression objects and dicts
cohort_def = CohortDefinition(
    name=cohort_name,
    description="Male patients diagnosed with type 2 diabetes mellitus who are under 40 years old at diagnosis",
    expression_type="SIMPLE_EXPRESSION", 
    expression=cohort_dict  # This works! The validator accepts dicts and falls back gracefully
)

# Create the cohort via WebAPI
saved_cohort = client.cohorts.create(cohort_def)
print(f"✅ Created cohort '{cohort_name}' with ID: {saved_cohort.id}")
```

### Check your Cohort 

```python
# Use the ID from the saved cohort
retrieved_cohort = client.cohorts.get(saved_cohort.id)
print("Retrieved cohort:")
print(f"ID: {retrieved_cohort.id}")
print(f"Name: {retrieved_cohort.name}")
print(f"Has expression: {retrieved_cohort.expression is not None}")

# If you want to see the full expression:
if retrieved_cohort.expression:
    print(f"Expression keys: {list(retrieved_cohort.expression.keys())}")
    print(f"Has ConceptSets: {'ConceptSets' in retrieved_cohort.expression}")
    print(f"Has PrimaryCriteria: {'PrimaryCriteria' in retrieved_cohort.expression}")
    print(f"Has InclusionRules: {'InclusionRules' in retrieved_cohort.expression}")
```




**Now this works perfectly**:

```python
# ✅ This now works with the fixed model
cohort_def = CohortDefinition(
    name=cohort_name,
    description="Built using proper models!",
    expressionType="SIMPLE_EXPRESSION", 
    expression=cohort_dict  # Dictionary accepted and preserved!
)
saved_cohort = client.cohorts.create(cohort_def)
```

**Backup approaches** (if you can't modify the model):

```python
# Manual payload - avoids Pydantic serialization issues
manual_payload = {
    "name": cohort_name,
    "description": "Built using proper models!",
    "expressionType": "SIMPLE_EXPRESSION",
    "expression": {
        "ConceptSets": [...],
        "PrimaryCriteria": {...},
        "InclusionRules": [...]
    }
}
response = client._http.post("/cohortdefinition/", json_body=manual_payload)
``` 

```python

# Create a minimal, clean payload
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
cohort_name = f"Type 2 Diabetes Males Under 40 - {timestamp}"

minimal_payload = {
    "name": cohort_name,
    "description": "Built using proper models!",
    "expressionType": "SIMPLE_EXPRESSION",
    "expression": {
        "ConceptSets": [
            {
                "id": 0,
                "name": "Type 2 Diabetes Mellitus",
                "expression": {
                    "items": [
                        {
                            "concept": {
                                "CONCEPT_ID": 201826,
                                "CONCEPT_NAME": "Type 2 diabetes mellitus",
                                "STANDARD_CONCEPT": "S",
                                "CONCEPT_CODE": "44054006",
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
        "InclusionRules": [],  # Start with empty inclusion rules
        "CensoringCriteria": []
    }
}

print("Minimal payload:")
print(json.dumps(minimal_payload, indent=2))

response = client._http.post("/cohortdefinition/", json_body=minimal_payload)
print("Create response:")
print(json.dumps(response, indent=2))

```

## Summary

This example demonstrates building a cohort definition from scratch using the unified OHDSI architecture. The cohort identifies Type 2 diabetes patients using the `ohdsi-cohort-schemas` models as the source of truth.


### Architecture Notes

**Creation**: Use unified models with `model_dump(by_alias=True)` to generate WebAPI-compatible JSON:
```python
from ohdsi_cohort_schemas import Concept, ConceptSetItem, ConceptSetExpression

# Create concept set using unified models
concept = Concept(concept_id=201826, concept_name="Type 2 diabetes mellitus", ...)
item = ConceptSetItem(concept=concept, include_descendants=True, ...)
concept_set_expr = ConceptSetExpression(items=[item])

# Use in WebAPI payload
"expression": concept_set_expr.model_dump(by_alias=True)  # Produces WebAPI format
```

**Retrieval**: Retrieved expressions are parsed into `CohortExpression` objects with Python field names:
- WebAPI `ConceptSets` → Python `concept_sets`
- WebAPI `PrimaryCriteria` → Python `primary_criteria`

**Validation**: Access retrieved data using Python field names:
```python
retrieved = client.cohorts.get(cohort_id)
if retrieved.expression.concept_sets:
    concept_sets = retrieved.expression.concept_sets
    for cs in concept_sets:
        items = cs.expression.items
        for item in items:
            concept_id = item.concept.concept_id  # Python field names
```
