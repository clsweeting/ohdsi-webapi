"""
PRACTICAL EXAMPLE: Finding Cardiovascular Disease Codes

This shows exactly how a user would find the right OMOP concept codes
for cardiovascular conditions using our OHDSI WebAPI client.

Usage:
    poetry run python examples/cardiovascular_code_finder.py
"""

import asyncio
from ohdsi_webapi import WebApiClient

async def find_cardiovascular_codes():
    """Complete example of finding cardiovascular codes."""
    
    # Step 1: Initialize client
    # (Make sure OHDSU_WEBAPI_BASE_URL is set in your .env file)
    client = WebApiClient()
    
    print("🔍 Finding Cardiovascular Disease Codes")
    print("=" * 45)
    
    try:
        # Step 2: Search for cardiovascular concepts
        print("\n1. Searching for 'cardiovascular' concepts...")
        concepts = client.vocabulary.search("cardiovascular")
        print(f"   Found {len(concepts)} total concepts")
        
        # Step 3: Filter to condition concepts only
        conditions = [c for c in concepts 
                     if c.domainId == 'Condition' and c.standardConcept == 'S']
        print(f"   Filtered to {len(conditions)} standard condition concepts")
        
        # Step 4: Show top cardiovascular concepts
        print("\\n2. Top cardiovascular condition concepts:")
        print("   " + "-" * 40)
        
        for i, concept in enumerate(conditions[:5]):
            print(f"   {i+1}. ID {concept.conceptId}: {concept.conceptName}")
            
            # Check how many subtypes this includes
            descendants = client.vocabulary.descendants(concept.conceptId)
            print(f"      → Includes {len(descendants)} more specific conditions")
            
            # Show a few examples
            if descendants and len(descendants) <= 10:
                print("      → Examples:", ", ".join([d.conceptName for d in descendants[:3]]))
            elif descendants:
                print("      → Examples:", ", ".join([d.conceptName for d in descendants[:2]]))
                print(f"        ...and {len(descendants) - 2} more")
            print()
        
        # Step 5: Search for specific common conditions
        print("3. Common specific cardiovascular conditions:")
        print("   " + "-" * 40)
        
        specific_searches = [
            "myocardial infarction",    # Heart attack
            "heart failure",            # Heart failure
            "atrial fibrillation",      # A-fib
            "cerebrovascular accident", # Stroke
            "coronary artery disease"   # CAD
        ]
        
        specific_codes = {}
        
        for search_term in specific_searches:
            search_results = await client.vocabulary.search(search_term)
            
            # Find the best standard condition concept
            best_match = None
            for concept in search_results:
                if (concept.domainId == 'Condition' and 
                    concept.standardConcept == 'S' and
                    search_term.lower() in concept.conceptName.lower()):
                    best_match = concept
                    break
            
            if best_match:
                specific_codes[search_term] = best_match
                print(f"   ✅ {search_term.replace('_', ' ').title()}")
                print(f"      ID: {best_match.conceptId}")
                print(f"      Name: {best_match.conceptName}")
                print()
        
        # Step 6: Show practical usage
        print("4. How to use these codes in your cohorts:")
        print("   " + "-" * 40)
        
        if conditions:
            broad_concept = conditions[0]
            print(f"   📊 For BROAD cardiovascular disease studies:")
            print(f"      concept_id = {broad_concept.conceptId}")
            print(f"      # {broad_concept.conceptName}")
            print(f"      # Includes ALL cardiovascular conditions")
            print()
        
        print(f"   🎯 For SPECIFIC condition studies:")
        for search_term, concept in specific_codes.items():
            condition_name = search_term.replace('_', ' ').title()
            print(f"      {condition_name}: {concept.conceptId}")
        
        print("\\n   💻 Code example:")
        print("      # Create concept set for broad CVD")
        if conditions:
            print(f"      cvd_cs = client.cohorts.create_concept_set(")
            print(f"          concept_id={broad_concept.conceptId},")
            print(f"          name='Cardiovascular Disease',")
            print(f"          include_descendants=True")
            print(f"      )")
        
        if specific_codes:
            first_code = list(specific_codes.values())[0]
            first_name = list(specific_codes.keys())[0].replace('_', ' ').title()
            print(f"\\n      # Create concept set for specific condition")
            print(f"      {first_name.lower().replace(' ', '_')}_cs = client.cohorts.create_concept_set(")
            print(f"          concept_id={first_code.conceptId},")
            print(f"          name='{first_name}'")
            print(f"      )")
        
        return conditions, specific_codes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure OHDSI_WEBAPI_BASE_URL is set in your .env file")
        return [], {}

async def demo_cohort_creation():
    """Show how to create a cohort with cardiovascular codes."""
    
    client = WebApiClient()
    
    print("\\n" + "=" * 50)
    print("🛠️  Demo: Creating Cardiovascular Cohort")
    print("=" * 50)
    
    try:
        # Check if we have data sources
        sources = client.sources.list()
        if not sources:
            print("ℹ️  No data sources available - showing concept creation only")
            
            # Just show concept set creation
            print("\\n📋 Creating cardiovascular concept sets:")
            
            # Broad cardiovascular disease
            broad_cs = client.cohorts.create_concept_set(
                concept_id=194990,
                name="All Cardiovascular Disease", 
                include_descendants=True
            )
            print(f"   ✅ {broad_cs['name']} (includes all subtypes)")
            
            # Specific condition
            mi_cs = client.cohorts.create_concept_set(
                concept_id=4329847,
                name="Myocardial Infarction"
            )
            print(f"   ✅ {mi_cs['name']} (heart attack only)")
            
            return
        
        source_key = sources[0].sourceKey
        print(f"📊 Using data source: {source_key}")
        
        # Create cardiovascular concept set
        cvd_cs = client.cohorts.create_concept_set(
            concept_id=194990,  # Broad cardiovascular disease
            name="Cardiovascular Disease"
        )
        
        print(f"\\n📋 Created concept set: {cvd_cs['name']}")
        
        # Create incremental cohort
        print("\\n🔄 Building cohort with incremental filters:")
        
        filters = [
            {"type": "gender", "gender": "male", "name": "Male patients"},
            {"type": "age", "min_age": 40, "name": "Age 40+"},
            {"type": "time_window", "concept_set_id": 0, "days_before": 1825, 
             "filter_name": "CVD in last 5 years"}
        ]
        
        results = await client.cohorts.build_incremental_cohort(
            source_key=source_key,
            base_name="CVD Study",
            concept_sets=[cvd_cs],
            filters=filters
        )
        
        print("\\n📈 Results:")
        for i, (cohort, count) in enumerate(results):
            step_name = cohort.name.split(" - ")[-1] if " - " in cohort.name else cohort.name
            print(f"   Step {i+1}: {count:,} patients - {step_name}")
            
            if i > 0:
                prev_count = results[i-1][1]
                reduction = prev_count - count
                pct = (reduction / prev_count * 100) if prev_count > 0 else 0
                print(f"           (-{reduction:,} patients, -{pct:.1f}%)")
        
        print("\\n✅ Cardiovascular cohort created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating cohort: {e}")

if __name__ == "__main__":
    async def main():
        # Find the codes
        conditions, specific_codes = await find_cardiovascular_codes()
        
        # Demo cohort creation
        await demo_cohort_creation()
        
        print(f"\\n🎯 Summary:")
        print(f"   • Found {len(conditions)} broad cardiovascular concepts")
        print(f"   • Found {len(specific_codes)} specific condition codes")
        print(f"   • Ready to use in your research!")
    
    asyncio.run(main())
