"""
Example: Using Exclusion Criteria in OHDSI Cohorts

This demonstrates how to use exclusion criteria to refine cohorts by 
excluding patients with certain conditions, medications, or procedures.

Common use cases:
- Exclude patients with cancer history for cardiac studies
- Exclude patients taking certain medications
- Exclude patients who died within X days (for outcome studies)
- Exclude patients with prior surgeries

Run with: poetry run python examples/exclusion_criteria_example.py
"""

import asyncio

from ohdsi_webapi import WebApiClient


async def exclusion_criteria_example():
    """Complete example showing inclusion + exclusion criteria."""

    client = WebApiClient()

    print("🚫 Exclusion Criteria Example")
    print("=" * 40)

    try:
        # Get data source
        sources = client.sources.list()
        if not sources:
            print("No data sources available")
            return

        source_key = sources[0].sourceKey
        print(f"📊 Using data source: {source_key}")

        # Step 1: Define concept sets
        print("\n1️⃣  Setting up concept sets...")

        # Primary condition: Heart failure
        heart_failure_cs = client.cohorts.create_concept_set(concept_id=444094, name="Heart Failure")  # Congestive heart failure

        # Exclusion conditions
        cancer_cs = client.cohorts.create_concept_set(
            concept_id=443392, name="Cancer", include_descendants=True  # Malignant neoplastic disease
        )

        chemotherapy_cs = client.cohorts.create_concept_set(
            concept_id=21601782, name="Chemotherapy Drugs", include_descendants=True  # Chemotherapy
        )

        cardiac_surgery_cs = client.cohorts.create_concept_set(
            concept_id=4336464, name="Cardiac Surgery", include_descendants=True  # Cardiac surgery
        )

        concept_sets = [heart_failure_cs, cancer_cs, chemotherapy_cs, cardiac_surgery_cs]
        print(f"   ✅ Created {len(concept_sets)} concept sets")

        # Step 2: Define inclusion criteria (what we want)
        inclusion_filters = [
            {"type": "gender", "gender": "male", "name": "Male patients"},
            {"type": "age", "min_age": 18, "max_age": 80, "name": "Age 18-80"},
            {"type": "time_window", "concept_set_id": 0, "days_before": 365, "filter_name": "Heart failure in last year"},
        ]

        # Step 3: Define exclusion criteria (what we don't want)
        exclusion_criteria = [
            {
                "type": "condition",
                "concept_set_id": 1,  # Cancer concept set
                "days_before": 1825,  # 5 years
                "name": "No cancer history (5 years)",
            },
            {
                "type": "drug",
                "concept_set_id": 2,  # Chemotherapy concept set
                "days_before": 365,  # 1 year
                "name": "No chemotherapy (1 year)",
            },
            {
                "type": "procedure",
                "concept_set_id": 3,  # Cardiac surgery concept set
                "days_before": 180,  # 6 months
                "name": "No recent cardiac surgery (6 months)",
            },
            {"type": "death", "days_after_index": 30, "name": "Survived at least 30 days"},
        ]

        print("\n2️⃣  Building cohort with inclusion + exclusion criteria...")

        # Step 4: Build incremental cohort with exclusions
        results = await client.cohorts.build_incremental_cohort(
            source_key=source_key,
            base_name="Heart Failure Study",
            concept_sets=concept_sets,
            filters=inclusion_filters,
            exclusions=exclusion_criteria,
        )

        # Step 5: Show results
        print("\n📈 Cohort Building Results:")
        print("-" * 50)

        for i, (cohort, count) in enumerate(results):
            step_name = cohort.name.split(" - ")[-1] if " - " in cohort.name else cohort.name
            print(f"Step {i+1:2}: {count:8,} patients - {step_name}")

            if i > 0:
                prev_count = results[i - 1][1]
                if "Exclude" in step_name:
                    excluded = prev_count - count
                    pct = (excluded / prev_count * 100) if prev_count > 0 else 0
                    print(f"           {excluded:8,} excluded (-{pct:.1f}%)")
                else:
                    reduction = prev_count - count
                    pct = (reduction / prev_count * 100) if prev_count > 0 else 0
                    print(f"           {reduction:8,} filtered (-{pct:.1f}%)")

        final_cohort = results[-1][0]
        final_count = results[-1][1]

        print(f"\n🎯 Final cohort: {final_count:,} patients")
        print(f"   Cohort ID: {final_cohort.id}")

        # Step 6: Show the power of exclusions
        base_count = results[0][1]  # Original count
        inclusion_count = None

        # Find where inclusion filters end and exclusions begin
        for i, (cohort, count) in enumerate(results):
            if "Exclude" in cohort.name:
                inclusion_count = results[i - 1][1]
                break

        if inclusion_count:
            included = base_count - inclusion_count
            excluded = inclusion_count - final_count

            print("\n📊 Impact Summary:")
            print(f"   Original population:     {base_count:8,}")
            print(f"   After inclusion filters: {inclusion_count:8,} ({included:,} removed)")
            print(f"   After exclusion criteria:{final_count:8,} ({excluded:,} excluded)")
            print(f"   Total reduction:         {base_count - final_count:8,} ({(base_count - final_count)/base_count*100:.1f}%)")

        return final_cohort

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure OHDSI_WEBAPI_BASE_URL is set in your .env file")


async def simple_exclusion_example():
    """Simple example showing basic exclusion concepts."""

    client = WebApiClient()

    print("\n" + "=" * 50)
    print("🔧 Simple Exclusion Example")
    print("=" * 50)

    # Example: Heart failure patients, but exclude those with cancer
    print("Scenario: Heart failure patients, excluding those with cancer history")

    # Create concept sets
    heart_failure_cs = client.cohorts.create_concept_set(444094, "Heart Failure")
    cancer_cs = client.cohorts.create_concept_set(443392, "Cancer", True)

    # Start with base expression
    base_expr = client.cohorts.create_base_cohort_expression([heart_failure_cs, cancer_cs])

    print("\n📋 Base expression created")
    print(f"   Concept sets: {len(base_expr['conceptSets'])}")
    print(f"   Inclusion rules: {len(base_expr['inclusionRules'])}")
    print(f"   Exclusion criteria: {len(base_expr['exclusionCriteria'])}")

    # Add exclusion for cancer history
    exclusion_expr = client.cohorts.add_exclusion_condition(
        base_expr, concept_set_id=1, days_before=1825, exclusion_name="No cancer in last 5 years"  # Cancer concept set  # 5 years
    )

    print("\n✅ Added cancer exclusion")
    print(f"   Inclusion rules: {len(exclusion_expr['inclusionRules'])}")
    print(f"   Exclusion criteria: {len(exclusion_expr['exclusionCriteria'])}")

    # Show what the exclusion looks like
    exclusion = exclusion_expr["exclusionCriteria"][0]
    criteria = exclusion["criteriaList"][0]
    window = criteria["startWindow"]

    print("\n🔍 Exclusion details:")
    print(f"   Condition: Concept set {criteria['criteria']['conditionOccurrence']['conceptSetId']}")
    print(f"   Time window: {window['start']['coeff']} to {window['end']['coeff']} days")
    print(f"   Logic: Exactly {criteria['occurrence']['count']} occurrences (exclusion)")

    return exclusion_expr


async def common_exclusion_patterns():
    """Show common exclusion patterns used in research."""

    print("\n" + "=" * 50)
    print("📚 Common Exclusion Patterns")
    print("=" * 50)

    client = WebApiClient()

    # Example base expression
    base_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")
    client.cohorts.create_base_cohort_expression([base_cs])

    patterns = [
        {
            "name": "Cancer History Exclusion",
            "description": "Exclude patients with any cancer in last 5 years",
            "method": "add_exclusion_condition",
            "params": {"concept_set_id": 1, "days_before": 1825},
        },
        {
            "name": "Pregnancy Exclusion",
            "description": "Exclude pregnant women",
            "method": "add_exclusion_condition",
            "params": {"concept_set_id": 2, "days_before": 280, "days_after": 0},
        },
        {
            "name": "Recent Hospitalization",
            "description": "Exclude recent hospital admissions (30 days)",
            "method": "add_exclusion_procedure",
            "params": {"concept_set_id": 3, "days_before": 30},
        },
        {
            "name": "Contraindicated Medication",
            "description": "Exclude patients on specific drugs",
            "method": "add_exclusion_drug",
            "params": {"concept_set_id": 4, "days_before": 90},
        },
        {
            "name": "Early Death",
            "description": "Exclude patients who died within 30 days",
            "method": "add_exclusion_death",
            "params": {"days_after_index": 30},
        },
    ]

    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['name']}")
        print(f"   Purpose: {pattern['description']}")
        print(f"   Method: client.cohorts.{pattern['method']}(expression, **params)")
        print(f"   Params: {pattern['params']}")
        print()

    print("💡 These patterns can be combined to create sophisticated cohorts!")
    print("   Each exclusion further refines your target population.")


if __name__ == "__main__":

    async def main():
        # Run comprehensive example
        await exclusion_criteria_example()

        # Show simple example
        await simple_exclusion_example()

        # Show common patterns
        await common_exclusion_patterns()

        print("\n🎯 Exclusion criteria help you create precise, clinically relevant cohorts!")

    asyncio.run(main())
