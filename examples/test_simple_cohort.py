"""
Simple cohort test with basic WebAPI operations
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Create unique suffix for cohort names to avoid conflicts
UNIQUE_SUFFIX = f"_{int(time.time())}"

def test_simple_cohort():
    """Test basic cohort operations without complex helpers."""
    
    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.models.cohort import CohortDefinition
    
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return
    
    print(f"🔗 Connecting to: {base_url}")
    
    try:
        client = WebApiClient(base_url=base_url)
        
        # Get available sources
        sources = client.sources.list()
        if not sources:
            print("❌ No data sources available")
            return
        
        source_key = sources[0].sourceKey
        print(f"📊 Using source: {sources[0].sourceName} ({source_key})")
        
        # Test simple concept search first
        print("\n🔍 Testing concept search...")
        try:
            # Try a very basic search
            concepts = client.vocabulary.search("hypertension", page_size=1)
            if concepts:
                concept = concepts[0]
                print(f"✅ Found concept: {concept.conceptId} - {concept.conceptName}")
                
                # Create a very simple cohort definition using this concept
                print(f"\n🎯 Creating simple cohort with concept {concept.conceptId}...")
                
                # Create concept set
                concept_set = client.cohorts.create_concept_set(
                    concept_id=concept.conceptId,
                    name=f"Test Concept{UNIQUE_SUFFIX}"
                )
                print(f"✅ Created concept set: {concept_set}")
                
                # Create base expression
                base_expression = client.cohorts.create_base_cohort_expression([concept_set])
                print(f"✅ Created base expression")
                
                # Create cohort definition
                cohort_def = CohortDefinition(
                    name=f"Simple Test Cohort{UNIQUE_SUFFIX}",
                    expression=base_expression
                )
                
                # Create cohort
                created_cohort = client.cohorts.create(cohort_def)
                print(f"✅ Created cohort: {created_cohort.id} - {created_cohort.name}")
                
                return created_cohort
                
            else:
                print("❌ No concepts found for 'hypertension'")
                return None
                
        except Exception as e:
            print(f"❌ Concept search failed: {e}")
            print("💡 Trying with a known concept ID instead...")
            
            # Fall back to a well-known concept ID (Type 2 diabetes)
            try:
                concept = client.vocabulary.get_concept(201826)  # Type 2 diabetes
                print(f"✅ Got concept by ID: {concept.conceptId} - {concept.conceptName}")
                
                # Create simple cohort with this concept
                concept_set = client.cohorts.create_concept_set(
                    concept_id=concept.conceptId,
                    name=f"Diabetes{UNIQUE_SUFFIX}"
                )
                
                base_expression = client.cohorts.create_base_cohort_expression([concept_set])
                
                cohort_def = CohortDefinition(
                    name=f"Diabetes Patients{UNIQUE_SUFFIX}",
                    expression=base_expression
                )
                
                created_cohort = client.cohorts.create(cohort_def)
                print(f"✅ Created cohort: {created_cohort.id} - {created_cohort.name}")
                
                return created_cohort
                
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                return None
    
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

if __name__ == "__main__":
    test_simple_cohort()
