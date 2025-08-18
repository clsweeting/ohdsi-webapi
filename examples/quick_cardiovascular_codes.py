"""
Quick Guide: Finding Cardiovascular Disease Codes

This shows the essential steps to find the right OMOP concept codes
for cardiovascular conditions using the OHDSI WebAPI client.
"""


async def find_cardiovascular_codes_quick():
    """Essential steps to find cardiovascular codes."""

    from ohdsi_webapi import OHDSIWebAPIClient

    client = OHDSIWebAPIClient()

    print("🔍 Step 1: Search for cardiovascular concepts")
    print("=" * 45)

    # Search for concepts
    concepts = client.vocabulary.search("cardiovascular")

    # Filter to get condition concepts only
    conditions = [c for c in concepts if c.domainId == "Condition" and c.standardConcept == "S"]

    print(f"Found {len(conditions)} cardiovascular condition concepts:")

    for i, concept in enumerate(conditions[:5]):
        print(f"{i+1}. ID {concept.concept_id}: {concept.concept_name}")

        # Check how broad this concept is
        descendants = client.vocabulary.descendants(concept.concept_id)
        print(f"   → Includes {len(descendants)} more specific conditions")
        print()

    print("\n🎯 Step 2: Common specific cardiovascular codes")
    print("=" * 45)

    # Search for specific well-known conditions
    specific_conditions = {
        "heart attack": "myocardial infarction",
        "heart failure": "heart failure",
        "stroke": "cerebrovascular accident",
        "coronary disease": "coronary artery disease",
    }

    found_codes = {}

    for common_name, medical_term in specific_conditions.items():
        search_results = client.vocabulary.search(medical_term)

        # Get the best match (standard condition concept)
        best_match = None
        for concept in search_results:
            if concept.domainId == "Condition" and concept.standardConcept == "S":
                best_match = concept
                break

        if best_match:
            found_codes[common_name] = best_match
            print(f"✅ {common_name.title()}: {best_match.concept_id}")
            print(f"   Medical name: {best_match.concept_name}")
            print()

    print("🛠️  Step 3: How to use these codes")
    print("=" * 35)

    # Show how to create concept sets
    print("For BROAD cardiovascular disease (all types):")
    if conditions:
        broad_concept = conditions[0]  # Usually the most general
        print(f"   concept_id = {broad_concept.concept_id}  # {broad_concept.concept_name}")
        print("   include_descendants = True  # Include all subtypes")

    print("\nFor SPECIFIC conditions:")
    for name, concept in found_codes.items():
        print(f"   {name}_concept_id = {concept.concept_id}")

    print("\nFor MULTIPLE specific conditions:")
    concept_ids = [concept.concept_id for concept in found_codes.values()]
    print(f"   cvd_concept_ids = {concept_ids}")

    return conditions[0] if conditions else None, found_codes


async def create_cvd_concept_set_example():
    """Show how to create concept sets with the codes we found."""

    from ohdsi_webapi import OHDSIWebAPIClient

    client = OHDSIWebAPIClient()

    print("\n💡 Example: Creating cardiovascular concept sets")
    print("=" * 50)

    # Example 1: Broad cardiovascular disease
    print("1. Broad cardiovascular disease concept set:")
    client.cohortdefs.create_concept_set(
        concept_id=194990, name="All Cardiovascular Disease", include_descendants=True  # "Cardiovascular disease"
    )
    print("   ✅ Includes ALL cardiovascular conditions")
    print(f"   Code: client.cohorts.create_concept_set({194990}, 'CVD', True)")

    # Example 2: Specific major conditions
    print("\n2. Specific major cardiovascular conditions:")

    major_cvd_codes = {"Heart Attack": 4329847, "Heart Failure": 444094, "Stroke": 381591, "Coronary Disease": 4110056}

    for name, code in major_cvd_codes.items():
        print(f"   {name}: {code}")

    print("\n   Code example:")
    print(f"   heart_attack_cs = client.cohorts.create_concept_set({4329847}, 'Heart Attack')")

    # Example 3: Usage in cohort
    print("\n3. Using in a cohort:")
    print(
        """
   # Create concept set
   cvd_cs = client.cohorts.create_concept_set(194990, "Cardiovascular Disease")
   
   # Build cohort with filters  
   results = await client.cohorts.build_incremental_cohort(
       source_key="your_source",
       base_name="CVD Study",
       concept_sets=[cvd_cs],
       filters=[
           {"type": "gender", "gender": "male"},
           {"type": "age", "min_age": 40}
       ]
   )
   
   # See results
   for i, (cohort, count) in enumerate(results):
       print(f"Step {i+1}: {count:,} patients")
   """
    )


# Usage example:
if __name__ == "__main__":
    import asyncio

    async def demo():
        broad_concept, specific_codes = await find_cardiovascular_codes_quick()
        await create_cvd_concept_set_example()

        print(f"\n🎯 Found codes for {len(specific_codes)} specific CVD conditions")
        print("   Ready to use in your cohort definitions!")

    asyncio.run(demo())
