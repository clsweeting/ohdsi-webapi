"""
Advanced Cohort Filters Example

This demonstrates the full range of human-friendly filter methods
available for building sophisticated OHDSI cohorts.

New filters include:
- Observation period requirements (continuous enrollment)
- Visit type filters (inpatient, outpatient, ER)
- Measurement filters (lab values, vital signs)
- Drug era filters (continuous medication exposure)
- Prior observation requirements (data quality)
- Multiple condition logic (ALL/ANY combinations)

Prerequisites:
1. Set OHDSI_WEBAPI_BASE_URL environment variable
2. Optionally set OHDSI_WEBAPI_AUTH_TOKEN if authentication required

Run with: poetry run python examples/advanced_cohort_filters.py
"""

import asyncio
import os

from dotenv import load_dotenv
from ohdsi_webapi import WebApiClient

# Load environment variables from .env file
load_dotenv()


async def advanced_filters_demo():
    """Demonstrate all the advanced filter types."""

    # Get WebAPI URL from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ Error: OHDSI_WEBAPI_BASE_URL environment variable not set")
        print("💡 Please set the environment variable:")
        print("   export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")
        print("   or add it to your .env file")
        return

    # Create client with environment configuration
    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    print("🔧 Advanced Cohort Filters Demo")
    print("=" * 40)
    print(f"📡 WebAPI URL: {base_url}")
    print(f"🔑 Authentication: {'Yes' if auth_token else 'No'}")

    try:
        # Get data source
        sources = client.source.sources()
        if not sources:
            print("No data sources available - showing filter creation only")
            show_filter_examples(client)
            return

        source_key = sources[0].source_key
        print(f"📊 Using data source: {source_key}")

        # Define concept sets for comprehensive example
        print("\n1️⃣  Creating concept sets...")
        concept_sets = [
            client.cohorts.create_concept_set(201826, "Type 2 Diabetes"),  # 0
            client.cohorts.create_concept_set(3655963, "Hemoglobin A1c"),  # 1 - HbA1c measurement
            client.cohorts.create_concept_set(1502826, "Metformin"),  # 2 - Metformin drug
            client.cohorts.create_concept_set(316866, "Hypertensive disease"),  # 3 - Hypertension
            client.cohorts.create_concept_set(314666, "Chronic kidney disease"),  # 4 - CKD
        ]
        print(f"   ✅ Created {len(concept_sets)} concept sets")

        # Define comprehensive filter set
        print("\n2️⃣  Setting up advanced filters...")
        filters = [
            # Basic demographics
            {"type": "gender", "gender": "male", "name": "Male patients"},
            {"type": "age", "min_age": 40, "max_age": 75, "name": "Age 40-75"},
            # Data quality requirements
            {"type": "prior_observation", "min_days": 365, "name": "1+ year prior data"},
            {
                "type": "observation_period",
                "days_before": 365,
                "days_after": 180,
                "name": "Continuous enrollment (1 year before, 6 months after)",
            },
            # Clinical criteria
            {"type": "time_window", "concept_set_id": 0, "days_before": 730, "filter_name": "Diabetes diagnosis in last 2 years"},
            # Lab value requirements
            {
                "type": "measurement",
                "concept_set_id": 1,
                "value_min": 7.0,
                "value_max": 10.0,
                "days_before": 180,
                "filter_name": "HbA1c 7-10% in last 6 months",
            },
            # Medication requirements
            {
                "type": "drug_era",
                "concept_set_id": 2,
                "era_length_min": 90,
                "days_before": 365,
                "filter_name": "Metformin for 90+ days in last year",
            },
            # Healthcare utilization
            {
                "type": "visit",
                "visit_concept_ids": [9202],
                "days_before": 90,  # Outpatient
                "filter_name": "Outpatient visit in last 90 days",
            },
            # Comorbidity requirements (must have ALL)
            {
                "type": "multiple_conditions",
                "concept_set_ids": [3, 4],
                "logic": "ALL",
                "days_before": 1095,
                "filter_name": "Has both hypertension AND kidney disease",
            },
        ]

        print(f"   ✅ Configured {len(filters)} advanced filters")

        # Build the cohort
        print("\n3️⃣  Building advanced cohort...")
        results = await client.cohorts.build_incremental_cohort(
            source_key=source_key, base_name="Advanced Diabetes Study", concept_sets=concept_sets, filters=filters
        )

        # Show results with detailed analysis
        print("\n📈 Advanced Cohort Results:")
        print("-" * 60)

        for i, (cohort, count) in enumerate(results):
            step_name = cohort.name.split(" - ")[-1] if " - " in cohort.name else cohort.name
            print(f"Step {i+1:2}: {count:8,} patients - {step_name}")

            if i > 0:
                prev_count = results[i - 1][1]
                reduction = prev_count - count
                pct = (reduction / prev_count * 100) if prev_count > 0 else 0
                print(f"           {reduction:8,} removed (-{pct:.1f}%)")

        # Analyze the impact
        analyze_filter_impact(results)

        return results[-1][0]

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Showing filter examples instead...")
        show_filter_examples(base_url)


def show_filter_examples(base_url: str):
    """Show examples of creating different filter types."""

    print("\n🛠️  Filter Type Examples")
    print("=" * 30)

    # Create client for examples
    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    # Create sample concept sets
    diabetes_cs = client.cohorts.create_concept_set(201826, "Diabetes")
    hba1c_cs = client.cohorts.create_concept_set(3655963, "HbA1c")

    # Base expression
    expr = client.cohorts.create_base_cohort_expression([diabetes_cs, hba1c_cs])

    print("1. Observation Period Filter:")
    obs_expr = client.cohorts.add_observation_period_filter(expr, 365, 180)
    print("   ✅ Added continuous enrollment requirement")

    print("\n2. Visit Type Filter:")
    visit_expr = client.cohorts.add_visit_filter(obs_expr, [9201, 9203], 30)  # Inpatient or ER
    print("   ✅ Added inpatient/ER visit requirement")

    print("\n3. Measurement Filter:")
    measurement_expr = client.cohorts.add_measurement_filter(visit_expr, 1, value_min=7.0, value_max=10.0, days_before=180)
    print("   ✅ Added HbA1c 7-10% requirement")

    print("\n4. Drug Era Filter:")
    drug_expr = client.cohorts.add_drug_era_filter(measurement_expr, 2, era_length_min=90, days_before=365)
    print("   ✅ Added 90+ day medication requirement")

    print("\n5. Prior Observation Filter:")
    prior_expr = client.cohorts.add_prior_observation_filter(drug_expr, 365)
    print("   ✅ Added 1-year prior data requirement")

    print("\n📊 Final expression structure:")
    print(f"   Concept sets: {len(prior_expr['conceptSets'])}")
    print(f"   Inclusion rules: {len(prior_expr['inclusionRules'])}")
    print("   Each rule refines the target population")


def analyze_filter_impact(results):
    """Analyze which filters had the biggest impact."""

    print("\n🔍 Filter Impact Analysis:")
    print("-" * 40)

    if len(results) < 2:
        return

    # Calculate impact of each filter
    impacts = []
    for i in range(1, len(results)):
        prev_count = results[i - 1][1]
        curr_count = results[i][1]
        reduction = prev_count - curr_count
        pct = (reduction / prev_count * 100) if prev_count > 0 else 0

        step_name = results[i][0].name.split(" - ")[-1]
        impacts.append((step_name, reduction, pct))

    # Sort by impact (highest reduction first)
    impacts.sort(key=lambda x: x[1], reverse=True)

    print("Most impactful filters (by patient reduction):")
    for i, (name, reduction, pct) in enumerate(impacts[:5]):
        print(f"  {i+1}. {name}")
        print(f"     Removed: {reduction:,} patients ({pct:.1f}%)")

    # Show final statistics
    initial_count = results[0][1]
    final_count = results[-1][1]
    total_reduction = initial_count - final_count
    total_pct = (total_reduction / initial_count * 100) if initial_count > 0 else 0

    print("\n📊 Overall Impact:")
    print(f"   Initial population:  {initial_count:8,}")
    print(f"   Final cohort:        {final_count:8,}")
    print(f"   Total reduction:     {total_reduction:8,} ({total_pct:.1f}%)")
    print(f"   Filters applied:     {len(impacts)}")


async def lab_values_example():
    """Specific example for lab value filtering."""

    print("\n" + "=" * 50)
    print("🧪 Lab Values Filtering Example")
    print("=" * 50)

    # Get WebAPI URL from environment
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set - showing code examples only")
        show_lab_value_code_examples()
        return

    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")
    if auth_token:
        from ohdsi_webapi.auth import BearerToken

        auth = BearerToken(auth_token)
        client = WebApiClient(base_url=base_url, auth=auth)
    else:
        client = WebApiClient(base_url=base_url)

    # Common lab value concept IDs
    lab_examples = [
        (3655963, "Hemoglobin A1c", 7.0, 10.0, "%"),
        (3004249, "LDL Cholesterol", 70, 190, "mg/dL"),
        (3027018, "Systolic BP", 120, 180, "mmHg"),
        (3004327, "Creatinine", 0.8, 2.0, "mg/dL"),
        (3024561, "Estimated GFR", 30, 90, "mL/min/1.73m²"),
    ]

    print("Common lab value filters:")

    diabetes_cs = client.cohorts.create_concept_set(201826, "Diabetes")
    client.cohorts.create_base_cohort_expression([diabetes_cs])

    for i, (concept_id, name, min_val, max_val, unit) in enumerate(lab_examples):
        print(f"\n{i+1}. {name} ({min_val}-{max_val} {unit}):")
        print(f"   Concept ID: {concept_id}")
        print("   Filter code:")
        print("   expression = client.cohorts.add_measurement_filter(")
        print(f"       expression, concept_set_id={i+1}, value_min={min_val}, value_max={max_val},")
        print(f"       days_before=180, filter_name='{name} {min_val}-{max_val}'")
        print("   )")

    print("\n💡 These filters help identify patients with specific lab value ranges")
    print("   Perfect for clinical studies with biomarker requirements!")


def show_lab_value_code_examples():
    """Show lab value filtering code examples when WebAPI is not available."""

    print("Common lab value filters (code examples):")

    lab_examples = [
        (3655963, "Hemoglobin A1c", 7.0, 10.0, "%"),
        (3004249, "LDL Cholesterol", 70, 190, "mg/dL"),
        (3027018, "Systolic BP", 120, 180, "mmHg"),
        (3004327, "Creatinine", 0.8, 2.0, "mg/dL"),
        (3024561, "Estimated GFR", 30, 90, "mL/min/1.73m²"),
    ]

    for i, (concept_id, name, min_val, max_val, unit) in enumerate(lab_examples):
        print(f"\n{i+1}. {name} ({min_val}-{max_val} {unit}):")
        print(f"   Concept ID: {concept_id}")
        print("   Filter code:")
        print("   expression = client.cohorts.add_measurement_filter(")
        print(f"       expression, concept_set_id={i+1}, value_min={min_val}, value_max={max_val},")
        print(f"       days_before=180, filter_name='{name} {min_val}-{max_val}'")
        print("   )")


def check_environment_setup():
    """Check if environment is properly configured."""

    print("🔧 Environment Setup Check")
    print("=" * 30)

    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    auth_token = os.getenv("OHDSI_WEBAPI_AUTH_TOKEN")

    if base_url:
        print(f"✅ OHDSI_WEBAPI_BASE_URL: {base_url}")
    else:
        print("❌ OHDSI_WEBAPI_BASE_URL: Not set")
        print("   Please set the environment variable:")
        print("   export OHDSI_WEBAPI_BASE_URL='http://localhost:8080/WebAPI'")

    if auth_token:
        print(f"✅ OHDSI_WEBAPI_AUTH_TOKEN: {'*' * 8} (set)")
    else:
        print("ℹ️  OHDSI_WEBAPI_AUTH_TOKEN: Not set (optional)")
        print("   Only needed if your WebAPI requires authentication")

    print(f"\n📄 .env file location: {os.path.join(os.getcwd(), '.env')}")
    env_exists = os.path.exists(".env")
    print(f"📄 .env file exists: {'Yes' if env_exists else 'No'}")

    if not env_exists:
        print("\n💡 Consider creating a .env file with:")
        print("   OHDSI_WEBAPI_BASE_URL=http://localhost:8080/WebAPI")
        print("   # OHDSI_WEBAPI_AUTH_TOKEN=your_token_if_needed")

    return base_url is not None


if __name__ == "__main__":

    async def main():
        # Check environment setup first
        if not check_environment_setup():
            print("\n❌ Environment not properly configured")
            print("🛠️  Showing code examples instead...\n")
            show_lab_value_code_examples()
            return

        try:
            # Main demo
            await advanced_filters_demo()

            # Lab values specific example
            await lab_values_example()

            print("\n🎯 With these advanced filters, you can build highly specific,")
            print("   clinically relevant cohorts that match real-world study criteria!")

        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            print("💡 This might be due to WebAPI connectivity or configuration issues")
            print("🔧 Please check your OHDSI_WEBAPI_BASE_URL and network connection")

    asyncio.run(main())
