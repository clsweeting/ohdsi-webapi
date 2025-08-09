#!/usr/bin/env python3
"""
Test script for cohort building functionality
"""

import os
import sys

# Add src to path so we can import the modules
src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)

from ohdsi_webapi.services.cohorts import CohortService


def test_cohort_helpers():
    """Test the cohort building helper methods."""

    # Mock HTTP client for testing
    class MockHttp:
        def get(self, path):
            return {}

        def post(self, path, json_body=None):
            return {"id": 123, "name": json_body.get("name", "test")}

        def put(self, path, json_body=None):
            return {}

        def delete(self, path):
            return {}

    service = CohortService(MockHttp())

    print("🧪 Testing cohort building helpers...")

    # Test 1: Concept set creation
    cs = service.create_concept_set(201826, "Type 2 Diabetes")
    assert cs["name"] == "Type 2 Diabetes"
    assert cs["expression"]["items"][0]["concept"]["conceptId"] == 201826
    print("✓ Concept set creation works")

    # Test 2: Base expression
    expr = service.create_base_cohort_expression([cs])
    assert len(expr["conceptSets"]) == 1
    assert expr["primaryCriteria"]["criteriaList"][0]["conditionOccurrence"]["conceptSetId"] == 0
    print("✓ Base cohort expression works")

    # Test 3: Gender filter
    male_expr = service.add_gender_filter(expr, "male")
    assert len(male_expr["inclusionRules"]) == 1
    assert male_expr["inclusionRules"][0]["name"] == "Male gender"
    print("✓ Gender filter works")

    # Test 4: Age filter
    age_expr = service.add_age_filter(male_expr, 40)
    assert len(age_expr["inclusionRules"]) == 2
    assert age_expr["inclusionRules"][1]["name"] == "Age >= 40"
    print("✓ Age filter works")

    # Test 5: Time window filter
    time_expr = service.add_time_window_filter(age_expr, 0, 730, 0, "Diabetes in last 2 years")
    assert len(time_expr["inclusionRules"]) == 3
    assert time_expr["inclusionRules"][2]["name"] == "Diabetes in last 2 years"
    print("✓ Time window filter works")

    print("\n✅ All cohort building tests passed!")

    # Show what a complete expression looks like
    print("\n📋 Sample cohort expression structure:")
    print(f"  - Concept sets: {len(time_expr['conceptSets'])}")
    print(f"  - Primary criteria: {len(time_expr['primaryCriteria']['criteriaList'])}")
    print(f"  - Inclusion rules: {len(time_expr['inclusionRules'])}")
    for i, rule in enumerate(time_expr["inclusionRules"]):
        print(f"    {i+1}. {rule['name']}")


if __name__ == "__main__":
    test_cohort_helpers()
