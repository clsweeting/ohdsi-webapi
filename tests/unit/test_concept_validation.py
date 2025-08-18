"""Test concept model validation to ensure examples work correctly."""

import pytest
from ohdsi_cohort_schemas.models.common import Concept
from ohdsi_cohort_schemas.models.concept_set import ConceptSetExpression, ConceptSetItem
from pydantic import ValidationError


def test_concept_minimal_required_fields():
    """Test that Concept can be created with just the required fields."""
    concept = Concept(
        concept_id=201826, concept_name="Type 2 diabetes mellitus", concept_code="44054006", vocabulary_id="SNOMED", domain_id="Condition"
    )

    assert concept.concept_id == 201826
    assert concept.concept_name == "Type 2 diabetes mellitus"
    assert concept.concept_code == "44054006"
    assert concept.vocabulary_id == "SNOMED"
    assert concept.domain_id == "Condition"

    # Optional fields should be None
    assert concept.standard_concept is None
    assert concept.concept_class_id is None
    assert concept.invalid_reason is None


def test_concept_with_all_fields():
    """Test that Concept works with all fields populated."""
    concept = Concept(
        concept_id=201826,
        concept_name="Type 2 diabetes mellitus",
        concept_code="44054006",
        vocabulary_id="SNOMED",
        domain_id="Condition",
        standard_concept="S",
        concept_class_id="Clinical Finding",
        invalid_reason=None,
        invalid_reason_caption=None,
        standard_concept_caption="Standard",
    )

    assert concept.concept_id == 201826
    assert concept.standard_concept == "S"
    assert concept.concept_class_id == "Clinical Finding"
    assert concept.standard_concept_caption == "Standard"


def test_concept_missing_required_fields():
    """Test that ValidationError is raised when required fields are missing."""

    # Missing concept_id
    with pytest.raises(ValidationError) as exc_info:
        Concept(concept_name="Type 2 diabetes mellitus", concept_code="44054006", vocabulary_id="SNOMED", domain_id="Condition")
    assert "CONCEPT_ID" in str(exc_info.value)  # Pydantic uses alias in error messages

    # Missing concept_name
    with pytest.raises(ValidationError) as exc_info:
        Concept(concept_id=201826, concept_code="44054006", vocabulary_id="SNOMED", domain_id="Condition")
    assert "CONCEPT_NAME" in str(exc_info.value)  # Pydantic uses alias in error messages

    # Missing concept_code
    with pytest.raises(ValidationError) as exc_info:
        Concept(concept_id=201826, concept_name="Type 2 diabetes mellitus", vocabulary_id="SNOMED", domain_id="Condition")
    assert "CONCEPT_CODE" in str(exc_info.value)  # Pydantic uses alias in error messages

    # Missing vocabulary_id
    with pytest.raises(ValidationError) as exc_info:
        Concept(concept_id=201826, concept_name="Type 2 diabetes mellitus", concept_code="44054006", domain_id="Condition")
    assert "VOCABULARY_ID" in str(exc_info.value)  # Pydantic uses alias in error messages

    # Missing domain_id
    with pytest.raises(ValidationError) as exc_info:
        Concept(concept_id=201826, concept_name="Type 2 diabetes mellitus", concept_code="44054006", vocabulary_id="SNOMED")
    assert "DOMAIN_ID" in str(exc_info.value)  # Pydantic uses alias in error messages


def test_concept_set_with_valid_concept():
    """Test that ConceptSetItem and ConceptSetExpression work with properly formed Concept."""
    concept = Concept(
        concept_id=201826, concept_name="Type 2 diabetes mellitus", concept_code="44054006", vocabulary_id="SNOMED", domain_id="Condition"
    )

    concept_item = ConceptSetItem(concept=concept, include_descendants=True, include_mapped=False, exclude=False)

    concept_set = ConceptSetExpression(items=[concept_item])

    assert len(concept_set.items) == 1
    assert concept_set.items[0].concept.concept_id == 201826
    assert concept_set.items[0].include_descendants is True


def test_concept_alias_mapping():
    """Test that Concept aliases work correctly for WebAPI compatibility."""
    # Create with Python names
    concept = Concept(
        concept_id=201826,
        concept_name="Type 2 diabetes mellitus",
        concept_code="44054006",
        vocabulary_id="SNOMED",
        domain_id="Condition",
        standard_concept="S",
    )

    # Should be able to serialize with aliases
    concept_dict = concept.model_dump(by_alias=True)

    assert concept_dict["CONCEPT_ID"] == 201826
    assert concept_dict["CONCEPT_NAME"] == "Type 2 diabetes mellitus"
    assert concept_dict["CONCEPT_CODE"] == "44054006"
    assert concept_dict["VOCABULARY_ID"] == "SNOMED"
    assert concept_dict["DOMAIN_ID"] == "Condition"
    assert concept_dict["STANDARD_CONCEPT"] == "S"

    # Should be able to create from aliased dict
    concept_from_alias = Concept(
        **{
            "CONCEPT_ID": 201826,
            "CONCEPT_NAME": "Type 2 diabetes mellitus",
            "CONCEPT_CODE": "44054006",
            "VOCABULARY_ID": "SNOMED",
            "DOMAIN_ID": "Condition",
            "STANDARD_CONCEPT": "S",
        }
    )

    assert concept_from_alias.concept_id == 201826
    assert concept_from_alias.standard_concept == "S"


def test_documentation_examples():
    """Test that the examples in documentation work correctly."""
    # Example from concept_sets.md
    diabetes_concept = Concept(
        concept_id=201826,
        concept_name="Type 2 diabetes mellitus",
        concept_code="44054006",  # Required field
        vocabulary_id="SNOMED",
        domain_id="Condition",
    )

    concept_item = ConceptSetItem(concept=diabetes_concept, include_descendants=True, include_mapped=False, exclude=False)

    concept_set = ConceptSetExpression(items=[concept_item])

    # Should not raise any validation errors
    assert concept_set.items[0].concept.concept_id == 201826

    # Example from helper_methods.md
    metformin_concept = Concept(
        concept_id=98061,
        concept_name="Metformin",
        concept_code="98061",  # Required field
        standard_concept="S",
        vocabulary_id="RxNorm",
        domain_id="Drug",
    )

    # Should not raise any validation errors
    assert metformin_concept.concept_id == 98061
    assert metformin_concept.concept_code == "98061"
