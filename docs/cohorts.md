# Cohorts

Cohorts define groups of persons meeting inclusion criteria over time. Thstatus = client.cohorts.poll_generation(cohort_id=123, source_key="EUNOMIA") WebAPI stores a cohort *definition* (JSON expression) and can *generate* the result set (cohort entry rows) in a target CDM source.


## Cohort Logic 

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
cohort = client.cohort(5)     # Equivalent to GET /cohort/{id}
print(cohort.name, cohort.expression_type)
```
The `expression` is a nested structure; this client stores it as a raw `dict` but can work with structured models from `ohdsi-cohort-schemas`.

```python
print(cohort) 

print(cohort.expression)
```




## Creating a Cohort Definition

Using the models from `ohdsi-cohort-schemas`:

```python
from ohdsi_webapi.models.cohort import CohortDefinition

from ohdsi_cohort_schemas import CohortExpression
from ohdsi_cohort_schemas.models.cohort import PrimaryCriteria
from ohdsi_cohort_schemas.models.common import ObservationWindow, Limit

# Using structured models (recommended)
observation_window = ObservationWindow(prior_days=0, post_days=0)
primary_criteria_limit = Limit(Type="All")  # Use alias field name

primary_criteria = PrimaryCriteria(
    criteria_list=[],
    observation_window=observation_window,
    primary_criteria_limit=primary_criteria_limit
)

expression = CohortExpression(
    primary_criteria=primary_criteria,
    concept_sets=[]
)

cohort_def = CohortDefinition(name="Sample Cohort", expression=expression)
created = client.cohorts.create(cohort_def)
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
cohort_def = CohortDefinition(name="Sample Cohort", expression=expression_dict)
created = client.cohorts.create(cohort_def)
```
The model validator gracefully handles both structured models and raw dicts.

> [!CAUTION]
> **Common ValidationError Fix:** If you get validation errors when creating models, check field names and avoid passing dictionaries as field values:
> 
> ```python
> # ❌ Wrong - passing dicts to model fields
> primary_criteria = PrimaryCriteria(
>     criteria_list=[],
>     observation_window={"prior_days": 0, "post_days": 0},  # Dict won't work
>     primary_criteria_limit={"type": "All"}  # Dict won't work
> )
> 
> # ❌ Wrong - incorrect field name (use alias for models without populate_by_name)
> primary_criteria_limit = Limit(type="All")  # Should be Type="All"
> 
> # ✅ Correct - use model instances with correct field names
> from ohdsi_cohort_schemas.models.common import ObservationWindow, Limit
> 
> observation_window = ObservationWindow(prior_days=0, post_days=0)
> primary_criteria_limit = Limit(Type="All")  # Use alias field name
> 
> primary_criteria = PrimaryCriteria(
>     criteria_list=[],
>     observation_window=observation_window,
>     primary_criteria_limit=primary_criteria_limit
> )
> ```


> [!WARNING]
> If you get a HTTP 409 error when trying to create a CohortDefinition, it indicates a conflict - usually
> as a result of using a name which has already been taken.  

## Updating a Cohort
```python
created.name = "Sample Cohort v2"
updated = client.cohorts.update(created.id, created)
```

## Deleting a Cohort
```python
client.cohorts.delete(updated.id)
```
Use with caution—irreversible.

## Generating a Cohort
You need a source key (from `client.source.sources()`) for a CDM with a results schema configured.
```python
sources = client.source.sources()
source_key = sources[0].source_key
status = client.cohorts.generate(cohort.id, source_key)
print(status.status)
```
This returns an initial status—often a background job.

## Polling for Completion
```python
# Poll for completion
final_status = client.cohorts.poll_generation(cohort_id=cohort.id, source_key=source_key)
print(final_status.status)
```
Terminal statuses: COMPLETED, FAILED, STOPPED.

## Inclusion Rule Stats
After a successful generation:
```python
stats = client.cohorts.inclusion_rules(cohort_id=cohort.id, source_key=source_key)
for rule in stats:
    print(rule.id, rule.name, rule.person_count)
```

## Counts
```python
counts = client.cohorts.counts(cohort_id=cohort.id)
for c in counts:
    print(c.cohort_definition_id, c.subject_count, c.entry_count)
```

## Error Handling
Generation can fail due to SQL translation or data issues. Wrap with try/except:
```python
from ohdsi_webapi.exceptions import WebApiError, JobTimeoutError
try:
    client.cohorts.poll_generation(cohort_id=cohort.id, source_key=source_key)
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
