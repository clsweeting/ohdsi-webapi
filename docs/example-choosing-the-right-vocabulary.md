# How to choose the right vocabulary

For conditions/diseases like "Type 2 diabetes", here's the decision process:

### 1. Look for Standard Clinical Terminologies

From the vocabularies available in the OHDSI WebAPI demo, the main candidates for conditions are:

- **SNOMED**: Systematic Nomenclature of Medicine 
- **ICD10CM**: International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS)
- **ICD9CM**: International Classification of Diseases, Ninth Revision, Clinical Modification (NCHS)

### 2. Try SNOMED first for conditions

SNOMED is usually the best choice for conditions because it's the most comprehensive, is the preferred standard for conditions in OMOP, and is hierarchical (has rich parent-child relationships, allowing you to include descendents).  It is also designed specifically for clinical terminology

### 3. Search through multiple vocabularies 

Try different vocabularies. 

For example, try SNOMED: 

```python 
# Search for type 2 diabetes in SNOMED vocabulary, Condition domain
snomed_results = client.vocabulary.search(
    query="type 2 diabetes",
    domain_id="Condition",
    vocabulary_id="SNOMED", 
    standard_concept="S"
)

print(f"SNOMED results: {len(snomed_results)}")
for concept in snomed_results[:5]:
    print(f"  - ID: {concept.concept_id}, Name: {concept.concept_name}")
```

Then compare to ICD10CM: 

```python 
# Search for type 2 diabetes in ICD10CM vocabulary, Condition domain  
icd10_results = client.vocabulary.search(
    query="type 2 diabetes",
    domain_id="Condition", 
    vocabulary_id="ICD10CM",
    standard_concept="S"
)

print(f"ICD10CM results: {len(icd10_results)}")
for concept in icd10_results[:5]:
    print(f"  - ID: {concept.concept_id}, Name: {concept.concept_name}")
```

This actually returns zero results for 'Type 2 diabetes'.


--------------

## Vocabulary Selection Cheat-sheet 

Data type |	First choice | 	Alternative
----------|--------------|--------------
Conditions/Diagnoses	 |	SNOMED	 |	ICD10CM
Procedures	 |	SNOMED	 |	CPT4, ICD10PCS
Drugs/Medications	 |	RxNorm	 |	NDC
Lab Tests/Measurements	 |	LOINC	 |	SNOMED
Demographics	 |	OMOP vocabularies	 |	(Gender, Race, etc.)


## If instructing an LLM, it should: 

- Always check available vocabularies first
- Try the standard vocabulary for the domain
- Fall back to alternatives if needed
- Explain the choice to the user

