# Standard vs. non-standard concepts 

In OMOP, concepts have a standard_concept field that can be:

- "S" = Standard concept
- "C" = Classification concept
- NULL/empty = Non-standard concept

## Why this matters

Standard concepts are the "official" concepts you should use for:

- Analysis and research
- Cohort definitions
- Mapping from source data


Non-standard concepts are often:

- Legacy codes (like old ICD-9 codes)
- Source-specific codes
- Concepts that map TO standard concepts
