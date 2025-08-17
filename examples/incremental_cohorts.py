#!/usr/bin/env python3
"""
Example: Incremental Cohort Building

This script demonstrates how to build a cohort incrementally, applying filters
one by one and seeing the population counts at each step.

Example scenario: "Males over 40 who have had diabetes in the last 2 years"

Prerequisites:
- Set OHDSI_WEBAPI_BASE_URL environment variable
- Optionally set OHDSI_WEBAPI_AUTH_TOKEN if authentication required

Run with: poetry run python examples/incremental_cohorts.py
"""

import asyncio
import os

from dotenv import load_dotenv
from ohdsi_webapi import WebApiClient
from ohdsi_webapi.models.cohort import CohortDefinition

# Load environment variables
load_dotenv()


async def build_diabetes_cohort_example():
    """Build a diabetes cohort step by step, showing counts at each stage."""

    # Get WebAPI configuration from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ Error: OHDSI_WEBAPI_BASE_URL environment variable not set")
        print("💡 Please set it to your OHDSI WebAPI URL, e.g.:")
        print("   export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")
        return

    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    # Choose your data source
    sources = client.source.sources()
    if not sources:
        print("No data sources available")
        return

    source_key = sources[0].sourceKey  # Use first available source
    print(f"Using data source: {source_key}")

    # 1. Create concept sets
    diabetes_concept_set = client.cohorts.create_concept_set(
        concept_id=201826, name="Type 2 Diabetes", include_descendants=True  # Type 2 diabetes mellitus
    )

    concept_sets = [diabetes_concept_set]

    # 2. Define incremental filters
    filters = [
        {"type": "gender", "gender": "male", "name": "Male gender"},
        {"type": "age", "min_age": 40, "name": "Age 40+"},
        {
            "type": "time_window",
            "concept_set_id": 0,  # References diabetes concept set
            "days_before": 730,  # 2 years
            "filter_name": "Diabetes diagnosis in last 2 years",
        },
    ]

    print("\n🔍 Building cohort incrementally...")
    print("=" * 50)

    # 3. Build cohort step by step
    try:
        results = await client.cohorts.build_incremental_cohort(
            source_key=source_key, base_name="Diabetes Males 40+", concept_sets=concept_sets, filters=filters
        )

        # 4. Display results
        print("\n📊 Cohort Building Results:")
        print("-" * 30)

        for i, (cohort, count) in enumerate(results):
            print(f"Step {i+1}: {cohort.name}")
            print(f"  Population: {count:,} patients")

            if i > 0:
                prev_count = results[i - 1][1]
                reduction = prev_count - count
                pct_reduction = (reduction / prev_count * 100) if prev_count > 0 else 0
                print(f"  Reduction: -{reduction:,} patients (-{pct_reduction:.1f}%)")

            print()

        # 5. Get detailed inclusion rule statistics for final cohort
        final_cohort = results[-1][0]
        print(f"📋 Detailed Statistics for: {final_cohort.name}")
        print("-" * 50)

        inclusion_stats = client.cohorts.inclusion_rules(final_cohort.id, source_key)
        for rule in inclusion_stats:
            print(f"✓ {rule.name}: {rule.personCount:,} people met this criteria")

        return final_cohort

    except Exception as e:
        print(f"❌ Error building cohort: {e}")
        return None


async def quick_diabetes_demo():
    """Quick demo showing the basic concept."""
    # Get WebAPI configuration from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ Error: OHDSI_WEBAPI_BASE_URL environment variable not set")
        return

    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    # Get available sources
    sources = client.source.sources()
    if not sources:
        print("No data sources available")
        return

    source_key = sources[0].sourceKey

    print(f"📍 Demo: Incremental filtering on {source_key}")
    print("=" * 40)

    # Manual step-by-step approach
    # Step 1: Create base diabetes cohort
    diabetes_cs = client.cohorts.create_concept_set(201826, "Type 2 Diabetes")
    base_expr = client.cohorts.create_base_cohort_expression([diabetes_cs])

    step1_cohort = CohortDefinition(name="Step 1: All diabetes patients", expression=base_expr)

    cohort1 = client.cohorts.create(step1_cohort)
    client.cohorts.generate(cohort1.id, source_key)
    client.cohorts.poll_generation(cohort1.id, source_key)
    counts1 = client.cohorts.counts(cohort1.id)

    print(f"1️⃣  All diabetes patients: {counts1[0].subjectCount if counts1 else 0:,}")

    # Step 2: Add male filter
    male_expr = client.cohorts.add_gender_filter(base_expr, "male")
    step2_cohort = CohortDefinition(name="Step 2: Male diabetes patients", expression=male_expr)

    cohort2 = client.cohorts.create(step2_cohort)
    client.cohorts.generate(cohort2.id, source_key)
    client.cohorts.poll_generation(cohort2.id, source_key)
    counts2 = client.cohorts.counts(cohort2.id)

    print(f"2️⃣  Male diabetes patients: {counts2[0].subjectCount if counts2 else 0:,}")

    # Step 3: Add age filter
    age_expr = client.cohorts.add_age_filter(male_expr, 40)
    step3_cohort = CohortDefinition(name="Step 3: Male diabetes patients 40+", expression=age_expr)

    cohort3 = client.cohorts.create(step3_cohort)
    client.cohorts.generate(cohort3.id, source_key)
    client.cohorts.poll_generation(cohort3.id, source_key)
    counts3 = client.cohorts.counts(cohort3.id)

    print(f"3️⃣  Male diabetes patients 40+: {counts3[0].subjectCount if counts3 else 0:,}")

    print("\n✅ Demo complete!")


if __name__ == "__main__":

    async def main():
        print("🏥 OHDSI Incremental Cohort Building Demo")
        print("========================================")

        # Check environment setup
        base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
        if not base_url:
            print("❌ Environment not configured properly")
            print("💡 Please set OHDSI_WEBAPI_BASE_URL environment variable")
            print("   Example: export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")
            print("\n💡 You can also create a .env file with:")
            print("   OHDSI_WEBAPI_BASE_URL=http://localhost:8080/WebAPI")
            print("   # OHDSI_WEBAPI_AUTH_TOKEN=your_token_if_needed")
            return

        print(f"📡 WebAPI URL: {base_url}")
        auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
        print(f"🔑 Authentication: {'Yes' if auth_token else 'No'}")

        try:
            # Run the full example
            print("\n📊 Running automated incremental cohort building...")
            await build_diabetes_cohort_example()

            print("\n" + "=" * 50)
            print("📊 Running quick manual demo...")

            # Run quick demo
            await quick_diabetes_demo()

            print("\n✅ All demos completed successfully!")
            print("💡 The automated method (first demo) is recommended for most use cases.")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Please check your WebAPI URL and network connection")

    asyncio.run(main())
