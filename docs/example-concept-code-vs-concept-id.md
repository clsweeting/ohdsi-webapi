

### Notes on Concept Code vs. Concept Id: 

Using the OHDSI Cohort Schema, we used this to define a concept: 

```
diabetes_concept = Concept(
    concept_id=201826,
    concept_name="Type 2 diabetes mellitus", 
    standard_concept="S",
    concept_code="44054006",
    concept_class_id="Clinical Finding",
    vocabulary_id="SNOMED",
    domain_id="Condition"
)
```

`concept_id`: This is OMOP's internal unique identifier for the concept across all vocabularies. It's globally unique in the OMOP standardized vocabularies.

`concept_code`: This is the original code from the source vocabulary (like SNOMED, ICD-10, etc.). This is what the original vocabulary system uses.


