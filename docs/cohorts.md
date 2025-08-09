# Cohorts

Cohorts define groups of persons meeting inclusion criteria over time. The WebAPI stores a cohort *definition* (JSON expression) and can *generate* the result set (cohort entry rows) in a target CDM source.

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
cohort = client.cohorts.get(5)
print(cohort.name, cohort.expressionType)
```
The `expression` is a nested structure; this client stores it as a raw `dict`.

## Creating a Cohort Definition
Minimal example (placeholder expression):
```python
from ohdsi_webapi.models.cohort import CohortDefinition

expression = {
  "PrimaryCriteria": {
    "CriteriaList": [],
    "ObservationWindow": {"PriorDays": 0, "PostDays": 0},
    "PrimaryCriteriaLimit": {"Type": "All"}
  },
  "ConceptSets": []
}
cohort_def = CohortDefinition(name="Sample Cohort", expression=expression)
created = client.cohorts.create(cohort_def)
print(created.id)
```
(Real expressions are typically composed using Atlas or a builder tool; future helpers may be added.)

## Updating a Cohort
```python
created.name = "Sample Cohort v2"
updated = client.cohorts.update(created)
```

## Deleting a Cohort
```python
client.cohorts.delete(updated.id)
```
Use with caution—irreversible.

## Generating a Cohort
You need a source key (from `client.sources.list()`) for a CDM with a results schema configured.
```python
source_key = client.sources.list()[0].sourceKey
status = client.cohorts.generate(cohort_id=cohort.id, source_key=source_key)
print(status.status)
```
This returns an initial status—often a background job.

## Polling for Completion
```python
final_status = client.cohorts.poll_generation(cohort_id=cohort.id, source_key=source_key, interval=10, timeout=1800)
print(final_status.status)
```
Terminal statuses: COMPLETED, FAILED, STOPPED.

## Inclusion Rule Stats
After a successful generation:
```python
stats = client.cohorts.inclusion_rules(cohort_id=cohort.id, source_key=source_key)
for rule in stats:
    print(rule.id, rule.name, rule.personCount)
```

## Counts
```python
counts = client.cohorts.counts(cohort_id=cohort.id)
for c in counts:
    print(c.cohortDefinitionId, c.subjectCount, c.entryCount)
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
