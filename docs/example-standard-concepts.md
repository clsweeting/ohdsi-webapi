# Standard vs. non-standard concepts 

In OMOP, concepts have a standard_concept field that can be:

- "S" = Standard concept
- "C" = Classification concept
- NULL/empty = Non-standard concept

## Why this matters

Standard concepts are consistent across all OMOP databases, so consider them the "official" concepts you should use for:

- Analysis and research
- Cohort definitions
- Mapping from source data

Non-standard concepts are often:

- Legacy codes (like old ICD-9 codes)
- Source-specific codes
- Concepts that map TO standard concepts


## Botton-line

Do NOT use non-standard concepts for analysis.  Map to standard concepts instead. 

Example: ICD-10 code `E11.9` maps to SNOMED `201826`

Always filter to standard concepts for analysis:

```python
standard_diabetes = client.vocabulary.search(
    query="diabetes",
    standard_concept="S",  # This is key!
    domain_id="Condition"
)
```
