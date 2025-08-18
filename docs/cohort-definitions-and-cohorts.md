# Cohort Definitions & Cohorts 

OHDSI WebAPI differentiates between Cohorts & Cohort Definitions: 

For Cohorts:
- `GET /cohort/id/` 

For Cohort Definitions: 
- `GET /cohortdefinition/` 
- `POST /cohortdefinition` 
- `GET/POST/PUT/DELETE /cohortdefinition/{id}` 
- etc

What's the difference ? 

`/cohortdefinition/` returns metadata about cohort definitions stored in the WebAPI database.
Think of it as: The blueprints or saved definitions of what a cohort is (e.g., “Patients with diabetes diagnosed after age 40”).
You call this when you want to know what cohorts exist in the system and see their definitions/metadata.

`/cohort/{id}` returns the actual cohort entities (the patients/subjects) that belong to a given cohort definition.
It returns the subject IDs, cohort start and end dates and the cohort definition ID which generated it. 
You call this when you want to see **who** is in the cohort (the rows in the COHORT table).


## Cohort Definition Logic 

Concept Sets are built from OMOP Vocabulary concepts. They're essentialy lists of standard concepts which can be referenced in Cohort Logic. See [Concept Sets](./concept_sets.md)

Concept Sets do NOT include: 
- Age ranges (e.g., “patients aged 40–65”)
- Gender (male/female/other)
- Race/Ethnicity
- Time-based constraints (e.g., “first diagnosis within past 12 months”)
- Logical conditions between concepts (“must have both X and Y”)

Those kinds of criteria are defined in the cohort logic in ATLAS/WebAPI, where you combine:
- Demographics
- Date/time filters
- Clinical events matched against Concept Sets

## Core Concepts
- Cohort Definition: JSON expression (similar to Atlas export) describing inclusion logic.
- Generation: Execution of the definition against a specific CDM source to materialize cohort entries.
- Inclusion Rule Statistics: Counts for each rule to understand attrition.
- Counts: Aggregate subject/entry counts post-generation.

## Setup
```python
from ohdsi_webapi import WebApiClient
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
```

## Fetch Existing Cohort Definition
```python
definition = client.cohortdefinition(5)     
print(definition.name, definition.expression_type)
```
The `expression` is a nested structure; this client stores it as a raw `dict` but can work with structured models from `ohdsi-cohort-schemas`.

```python
print(definition) 

print(definition.expression)
```




## Creating a Cohort Definition

Using the models from `ohdsi-cohort-schemas`:

```python
from ohdsi_webapi.models.cohort import CohortDefinition
from datetime import datetime

from ohdsi_cohort_schemas import CohortExpression
from ohdsi_cohort_schemas.models.cohort import PrimaryCriteria
from ohdsi_cohort_schemas.models.common import ObservationWindow, Limit

# Using structured models (recommended)
observation_window = ObservationWindow(prior_days=0, post_days=0)
primary_criteria_limit = Limit(type="All")

primary_criteria = PrimaryCriteria(
    criteria_list=[],
    observation_window=observation_window,
    primary_criteria_limit=primary_criteria_limit
)

expression = CohortExpression(
    primary_criteria=primary_criteria,
    concept_sets=[]
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
cohort_def = CohortDefinition(name=f"Sample Cohort {timestamp}", expression=expression)
created = client.cohortdefinition_create(cohort_def)
print(created.id)

# Or using dict format (also supported)
expression_dict = {
  "PrimaryCriteria": {
    "CriteriaList": [],
    "ObservationWindow": {"PriorDays": 0, "PostDays": 0},
    "PrimaryCriteriaLimit": {"Type": "All"}
  },
  "ConceptSets": []
}
cohort_def = CohortDefinition(name=f"Sample Cohort Dict {timestamp}", expression=expression_dict)
created = client.cohortdefinition_create(cohort_def)
```
The model validator gracefully handles both structured models and raw dicts.


> [!WARNING]
> If you get a HTTP 409 error when trying to create a CohortDefinition, it indicates a conflict - usually
> as a result of using a name which has already been taken.  

## Updating a Cohort
```python
created.name = f"Sample Cohort v2 {timestamp}"
updated = client.cohortdefinition_update(created)
```

## Deleting a Cohort
```python
client.cohortdefinition_delete(updated.id)
```
Use with caution—irreversible.

## Generating a Cohort
You need a source key (from `client.source.sources()`) for a CDM with a results schema configured.

```python
sources = client.source.sources()
source_key = sources[0].source_key
job = client.cohortdefinition_generate(cohort.id, source_key)

# result should be something like: 
# execution_id=80425 status='STARTING' start_time=None end_time=None
print(job.status)
print(job.execution_id)
```


## Polling for Completion

```python
# Poll for completion
final_status = client.cohortdefs.poll_generation(cohort_id=cohort.id, source_key=source_key)
print(final_status.status)
```
Terminal statuses: COMPLETED, FAILED, STOPPED.

## Inclusion Rule Stats
After a successful generation:

```python
stats = client.cohortdefs.inclusion_rules(cohort_id=cohort.id, source_key=source_key)
for rule in stats:
    print(rule.id, rule.name, rule.person_count)
```

## Counts

```python
counts = client.cohortdefs.counts(cohort_id=cohort.id)
for c in counts:
    print(c.cohort_definition_id, c.subject_count, c.entry_count)
```

## Error Handling
Generation can fail due to SQL translation or data issues. Wrap with try/except:

```python
from ohdsi_webapi.exceptions import WebApiError, JobTimeoutError

try:
    client.cohortdefs.poll_generation(cohort_id=cohort.id, source_key=source_key)
except JobTimeoutError:
    print("Generation timed out")
except WebApiError as e:
    print("Generation failed", e.status_code)
```

## Best Practices
- Reuse concept sets: Avoid embedding large literal code lists in cohort definition; reference concept sets.
- Version cohort definitions (export JSON and track changes in VCS).
- Monitor inclusion rule attrition to validate logic.
- Avoid generating against production-size CDM during rapid iteration; use a small sample environment.

## Roadmap Enhancements (Future)
- Builder utilities to programmatically compose criteria.
- Streaming retrieval of large inclusion stats.
- Export helpers for person-level entries (DataFrame integration).
