"""
Test basic connection to OHDSI WebAPI demo server
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test basic connection and list available endpoints."""
    
    from ohdsi_webapi import WebApiClient
    
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return
    
    print(f"🔗 Connecting to: {base_url}")
    
    try:
        client = WebApiClient(base_url=base_url)
        
        # Test basic info
        print("\n📊 WebAPI Info:")
        info = client.info.get()
        print(f"Version: {getattr(info, 'version', 'Unknown')}")
        
        # Test sources
        print("\n📊 Available Sources:")
        sources = client.sources.list()
        for source in sources:
            print(f"- {source.sourceName} (key: {source.sourceKey})")
        
        # Test vocabulary
        print("\n📊 Vocabulary Info:")
        try:
            domains = client.vocabulary.domains()
            print(f"Available domains: {len(domains) if domains else 'Unknown'}")
            if domains:
                print(f"  Sample domains: {[d.get('domainName', d.get('domainId', 'Unknown'))[:20] for d in domains[:3]]}")
        except Exception as e:
            print(f"Vocabulary domains error: {e}")
        
        # Test concept search
        print("\n📊 Testing concept search:")
        try:
            concepts = client.vocabulary.search("diabetes", page_size=3)
            print(f"Found {len(concepts)} diabetes concepts:")
            for concept in concepts[:3]:
                print(f"  - {concept.conceptId}: {concept.conceptName}")
        except Exception as e:
            print(f"Concept search error: {e}")
        
        print("\n✅ Basic connection successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
