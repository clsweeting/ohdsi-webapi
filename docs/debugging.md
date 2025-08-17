# Curl request to create a cohort 

```
curl -X POST "https://atlas-demo.ohdsi.org/WebAPI/cohortdefinition" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Curl Test - Null Fields",
    "description": "Testing with null fields like unified models",
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
                  "CONCEPT_CLASS_ID": null,
                  "VOCABULARY_ID": "SNOMED",
                  "DOMAIN_ID": "Condition",
                  "INVALID_REASON": null,
                  "INVALID_REASON_CAPTION": null,
                  "STANDARD_CONCEPT_CAPTION": null
                },
                "includeDescendants": true,
                "includeMapped": false,
                "isExcluded": false
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
      "InclusionRules": [],
      "CensoringCriteria": []
    }
  }' | jq .
  ```
  