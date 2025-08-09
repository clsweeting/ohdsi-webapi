"""
Simple Cohort Building Example

This shows how to answer questions like:
"How many males over 40 have had diabetes in the last 2 years?"

And track the counts as you apply each filter incrementally.

Prerequisites:
- Set OHDSI_WEBAPI_BASE_URL environment variable
- Optionally set OHDSI_WEBAPI_AUTH_TOKEN if authentication required

Run with: poetry run python examples/simple_cohort_example.py
"""

import os
import time

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create unique suffix for cohort names to avoid conflicts
UNIQUE_SUFFIX = f"_{int(time.time())}"


async def example_incremental_cohort():
    """Example showing step-by-step cohort building with counts."""

    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.models.cohort import CohortDefinition

    # Get WebAPI configuration from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ Error: OHDSI_WEBAPI_BASE_URL environment variable not set")
        print("💡 Please set the environment variable:")
        print("   export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")
        print("   or add it to your .env file")
        return None

    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    # Get data source
    sources = client.sources.list()
    source_key = sources[0].source_key  # Use first available

    print("Building cohort: Males over 40 with diabetes in last 2 years")
    print("=" * 60)

    # 1. Create concept set for diabetes
    diabetes_concepts = client.cohorts.create_concept_set(concept_id=201826, name="Diabetes Type 2")  # Type 2 diabetes

    # 2. Start with base cohort (just diabetes)
    base_expression = client.cohorts.create_base_cohort_expression([diabetes_concepts])

    cohort_base = CohortDefinition(name=f"All diabetes patients{UNIQUE_SUFFIX}", expression=base_expression)

    # Create and generate
    c1 = client.cohorts.create(cohort_base)
    client.cohorts.generate(c1.id, source_key)
    client.cohorts.poll_generation(c1.id, source_key)
    counts1 = client.cohorts.counts(c1.id)

    print(f"Step 1 - All diabetes patients: {counts1[0].subject_count:,}")

    # 3. Add male filter
    male_expression = client.cohorts.add_gender_filter(base_expression, "male")

    cohort_male = CohortDefinition(name=f"Male diabetes patients{UNIQUE_SUFFIX}", expression=male_expression)

    c2 = client.cohorts.create(cohort_male)
    client.cohorts.generate(c2.id, source_key)
    client.cohorts.poll_generation(c2.id, source_key)
    counts2 = client.cohorts.counts(c2.id)

    print(f"Step 2 - Male diabetes patients: {counts2[0].subject_count:,}")

    # 4. Add age filter (40+)
    age_expression = client.cohorts.add_age_filter(male_expression, 40)

    cohort_age = CohortDefinition(name=f"Male diabetes patients 40+{UNIQUE_SUFFIX}", expression=age_expression)

    c3 = client.cohorts.create(cohort_age)
    client.cohorts.generate(c3.id, source_key)
    client.cohorts.poll_generation(c3.id, source_key)
    counts3 = client.cohorts.counts(c3.id)

    print(f"Step 3 - Male diabetes patients 40+: {counts3[0].subject_count:,}")

    # 5. Add time window (last 2 years)
    final_expression = client.cohorts.add_time_window_filter(
        age_expression, concept_set_id=0, days_before=730, filter_name="Diabetes in last 2 years"  # diabetes concept set  # 2 years
    )

    cohort_final = CohortDefinition(name=f"Male diabetes patients 40+ (last 2 years){UNIQUE_SUFFIX}", expression=final_expression)

    c4 = client.cohorts.create(cohort_final)
    client.cohorts.generate(c4.id, source_key)
    client.cohorts.poll_generation(c4.id, source_key)
    counts4 = client.cohorts.counts(c4.id)

    print(f"Step 4 - Final cohort: {counts4[0].subject_count:,}")

    # Show the impact of each filter
    print("\nFilter Impact:")
    print(f"Male filter: -{counts1[0].subject_count - counts2[0].subject_count:,} patients")
    print(f"Age 40+ filter: -{counts2[0].subject_count - counts3[0].subject_count:,} patients")
    print(f"Time window filter: -{counts3[0].subject_count - counts4[0].subject_count:,} patients")

    return c4


# Alternative: Use the automated helper
async def example_automated():
    """Same result using the automated helper method."""

    from ohdsi_webapi import WebApiClient

    # Get WebAPI configuration from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ Error: OHDSI_WEBAPI_BASE_URL environment variable not set")
        return None

    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)
    sources = client.sources.list()
    source_key = sources[0].source_key

    # Define what we want
    diabetes_cs = client.cohorts.create_concept_set(201826, "Diabetes Type 2")

    filters = [
        {"type": "gender", "gender": "male", "name": "Male"},
        {"type": "age", "min_age": 40, "name": "Age 40+"},
        {"type": "time_window", "concept_set_id": 0, "days_before": 730, "filter_name": "Diabetes in last 2 years"},
    ]

    # Build incrementally - this does all the work for us
    results = await client.cohorts.build_incremental_cohort(
        source_key=source_key, base_name=f"Males 40+ Diabetes{UNIQUE_SUFFIX}", concept_sets=[diabetes_cs], filters=filters
    )

    print("Automated Results:")
    for i, (cohort, count) in enumerate(results):
        print(f"Step {i+1}: {count:,} patients - {cohort.name}")

    return results[-1][0]  # Return final cohort


if __name__ == "__main__":
    import asyncio

    async def main():
        print("🔧 Simple Cohort Building Example")
        print("=" * 40)

        # Check environment setup
        base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
        if not base_url:
            print("❌ Environment not configured properly")
            print("💡 Please set the environment variable:")
            print("   OHDSI_WEBAPI_BASE_URL")
            print("   Example: export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")
            return

        print(f"📡 WebAPI URL: {base_url}")

        try:
            print("\n📊 Method 1: Step-by-step manual building")
            print("-" * 50)
            await example_incremental_cohort()

            print("\n📊 Method 2: Automated incremental building")
            print("-" * 50)
            await example_automated()

            print("\n✅ Both methods should produce the same results!")
            print("💡 The automated method is simpler for most use cases.")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Please check your WebAPI URL and network connection")

    asyncio.run(main())
