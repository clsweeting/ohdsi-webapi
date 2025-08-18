#!/usr/bin/env python3
"""
Practical Example: Finding the Right Codes for 'Cardiovascular Disease'

This script shows step-by-step how a user would explore and find 
the appropriate OMOP concept codes for cardiovascular conditions.

Run with: poetry run python examples/find_cardiovascular_codes.py
"""

import asyncio
import os
import sys

# Add src to path for development
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, src_path)

from ohdsi_webapi import OHDSIWebAPIClient


async def find_cardiovascular_codes():
    """Step-by-step guide to finding cardiovascular disease codes."""

    client = OHDSIWebAPIClient()

    print("🔍 Finding Cardiovascular Disease Codes")
    print("=" * 50)

    # Step 1: Search for cardiovascular concepts
    print("Step 1: Search for 'cardiovascular' concepts...")
    cvd_concepts = await client.vocabulary.search("cardiovascular")

    print(f"Found {len(cvd_concepts)} concepts matching 'cardiovascular'")
    print("\nTop 10 results:")
    print("-" * 40)

    for i, concept in enumerate(cvd_concepts[:10]):
        print(f"{i+1:2}. ID {concept.concept_id}: {concept.concept_name}")
        print(f"     Domain: {concept.domainId}, Standard: {concept.standardConcept}")
        print()

    # Step 2: Look for high-level parent concepts
    print("\nStep 2: Finding high-level cardiovascular concepts...")

    # Filter for condition domain and standard concepts
    condition_concepts = [c for c in cvd_concepts if c.domainId == "Condition" and c.standardConcept == "S"]

    print(f"Found {len(condition_concepts)} standard condition concepts")

    # Look for broader terms (shorter names, likely parents)
    broad_concepts = [c for c in condition_concepts if len(c.concept_name.split()) <= 4 and "disease" in c.concept_name.lower()]

    print(f"\nBroad cardiovascular concepts ({len(broad_concepts)}):")
    print("-" * 50)

    for concept in broad_concepts[:5]:
        print(f"🎯 {concept.concept_id}: {concept.concept_name}")

        # Check how many descendants this includes
        descendants = await client.vocabulary.descendants(concept.concept_id)
        print(f"   → Includes {len(descendants)} more specific conditions")

        # Show a few examples
        if descendants:
            examples = descendants[:3]
            for ex in examples:
                print(f"      • {ex.concept_name}")
            if len(descendants) > 3:
                print(f"      • ...and {len(descendants) - 3} more")
        print()

    # Step 3: Show specific common conditions
    print("\nStep 3: Common specific cardiovascular conditions...")
    print("-" * 50)

    # Search for specific well-known conditions
    specific_searches = ["myocardial infarction", "heart failure", "atrial fibrillation", "coronary artery disease", "stroke"]

    specific_concepts = {}
    for search_term in specific_searches:
        concepts = await client.vocabulary.search(search_term)
        # Get the most relevant standard concept
        standard_concepts = [c for c in concepts if c.standardConcept == "S" and c.domainId == "Condition"]
        if standard_concepts:
            # Take the first one (usually most relevant)
            specific_concepts[search_term] = standard_concepts[0]

    for search_term, concept in specific_concepts.items():
        print(f"🔸 {search_term.title()}")
        print(f"   ID: {concept.concept_id}")
        print(f"   Name: {concept.concept_name}")

        # Check descendants
        descendants = await client.vocabulary.descendants(concept.concept_id)
        print(f"   Subtypes: {len(descendants)} descendants")
        print()

    # Step 4: Practical recommendations
    print("\nStep 4: Practical Recommendations")
    print("-" * 40)

    print("For BROAD cardiovascular disease studies:")
    if broad_concepts:
        main_cvd = broad_concepts[0]  # Usually "Cardiovascular disease"
        print(f"✅ Use concept {main_cvd.concept_id}: {main_cvd.concept_name}")
        print("   → Includes all cardiovascular conditions")

    print("\nFor SPECIFIC condition studies:")
    for search_term, concept in specific_concepts.items():
        print(f"✅ {search_term.title()}: Use concept {concept.concept_id}")

    print("\nFor CUSTOM combinations:")
    print("✅ Create concept set with multiple specific conditions")
    print("   → Pick 3-5 most relevant conditions for your study")

    return broad_concepts, specific_concepts


async def create_cardiovascular_concept_sets():
    """Show how to create concept sets from the codes we found."""

    client = OHDSIWebAPIClient()

    print("\n" + "=" * 60)
    print("🛠️  Creating Cardiovascular Concept Sets")
    print("=" * 60)

    # Method 1: Broad cardiovascular disease
    print("Method 1: Broad cardiovascular disease concept set")
    broad_cs = client.cohortdefs.create_concept_set(
        concept_id=194990, name="All Cardiovascular Disease", include_descendants=True  # "Cardiovascular disease"
    )
    print(f"✅ Created: {broad_cs['name']}")
    print(f"   Concept ID: {broad_cs['expression']['items'][0]['concept']['conceptId']}")
    print(f"   Includes descendants: {broad_cs['expression']['items'][0]['includeDescendants']}")

    # Method 2: Specific major conditions
    print("\nMethod 2: Major cardiovascular conditions concept set")

    # We'd normally get these from our search above, but here are common ones:
    major_cvd_concepts = [
        (4329847, "Myocardial infarction"),
        (316866, "Hypertensive heart disease"),
        (381591, "Cerebrovascular accident"),
        (4110056, "Chronic ischemic heart disease"),
        (444094, "Congestive heart failure"),
    ]

    # Create individual concept sets for each
    major_concept_sets = []
    for concept_id, name in major_cvd_concepts:
        cs = client.cohortdefs.create_concept_set(concept_id, name, include_descendants=True)
        major_concept_sets.append(cs)
        print(f"✅ Created: {name} (ID: {concept_id})")

    # Method 3: Combined concept set (multiple concepts in one set)
    print("\nMethod 3: Custom combined concept set")
    combined_expression = {"id": 0, "name": "Major Cardiovascular Conditions", "expression": {"items": []}}

    # Add all major conditions to one concept set
    for concept_id, name in major_cvd_concepts:
        item = {
            "concept": {
                "conceptId": concept_id,
                "conceptName": name,
                "includeDescendants": True,
                "includeMapped": False,
                "isExcluded": False,
            }
        }
        combined_expression["expression"]["items"].append(item)

    print(f"✅ Created combined set with {len(major_cvd_concepts)} conditions")
    print("   This single concept set includes all major CVD conditions")

    return broad_cs, major_concept_sets, combined_expression


async def test_cardiovascular_cohort():
    """Show how to use the cardiovascular codes in a real cohort."""

    print("\n" + "=" * 60)
    print("🧪 Testing Cardiovascular Cohort Creation")
    print("=" * 60)

    client = OHDSIWebAPIClient()

    try:
        # Get available data sources
        sources = client.source.sources()
        if not sources:
            print("❌ No data sources available for testing")
            return

        source_key = sources[0].source_key
        print(f"📊 Using data source: {source_key}")

        # Create cardiovascular concept set
        cvd_cs = client.cohortdefs.create_concept_set(concept_id=194990, name="Cardiovascular Disease")  # Broad cardiovascular disease

        # Test different cohort approaches
        approaches = [
            {"name": "All CVD patients", "filters": []},
            {"name": "Male CVD patients 40+", "filters": [{"type": "gender", "gender": "male"}, {"type": "age", "min_age": 40}]},
            {
                "name": "CVD in last 5 years",
                "filters": [
                    {"type": "gender", "gender": "male"},
                    {"type": "age", "min_age": 40},
                    {"type": "time_window", "concept_set_id": 0, "days_before": 1825},
                ],
            },
        ]

        print("\n📈 Cohort size comparison:")
        print("-" * 30)

        for approach in approaches:
            try:
                results = await client.cohortdefs.build_incremental_cohort(
                    source_key=source_key, base_name=f"CVD Study - {approach['name']}", concept_sets=[cvd_cs], filters=approach["filters"]
                )

                final_count = results[-1][1]
                print(f"{approach['name']:25} → {final_count:,} patients")

            except Exception as e:
                print(f"{approach['name']:25} → Error: {e}")

        print("\n✅ Cardiovascular cohort testing complete!")

    except Exception as e:
        print(f"❌ Error testing cohort: {e}")
        print("💡 Make sure you have OHDSI_WEBAPI_BASE_URL set in your .env file")


if __name__ == "__main__":
    print("🏥 OHDSI Cardiovascular Code Finding Guide")
    print("==========================================")

    async def main():
        # Step 1: Find the codes
        broad_concepts, specific_concepts = await find_cardiovascular_codes()

        # Step 2: Show how to create concept sets
        broad_cs, major_sets, combined_cs = await create_cardiovascular_concept_sets()

        # Step 3: Test with real cohort (if data source available)
        await test_cardiovascular_cohort()

        print(f"\n🎯 Summary: Found {len(specific_concepts)} specific CVD concepts")
        print("   Use these concept IDs in your cohort definitions!")

    asyncio.run(main())
