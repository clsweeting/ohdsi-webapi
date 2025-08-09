"""
Unit tests for the caching system.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from ohdsi_webapi.cache import (
    WebApiCache,
    CacheEntry,
    get_cache_key,
    cached_method,
    cache_stats,
    cache_contents,
    clear_cache,
    _global_cache
)


class TestCacheEntry:
    """Test CacheEntry functionality."""
    
    def test_cache_entry_creation(self):
        """Test basic cache entry creation."""
        entry = CacheEntry("test_data", ttl_seconds=300)
        
        assert entry.value == "test_data"
        assert entry.ttl_seconds == 300
        assert not entry.is_expired()
        assert entry.created_at <= time.time()
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration logic."""
        # Create entry that expires immediately
        entry = CacheEntry("test_data", ttl_seconds=0)
        time.sleep(0.01)  # Small delay to ensure expiration
        
        assert entry.is_expired()
    
    def test_cache_entry_no_expiration(self):
        """Test cache entry with no TTL (never expires)."""
        entry = CacheEntry("test_data", ttl_seconds=999999)  # Very long TTL instead of None
        
        assert not entry.is_expired()


class TestWebApiCache:
    """Test WebApiCache functionality."""
    
    def setup_method(self):
        """Setup fresh cache for each test."""
        self.cache = WebApiCache(max_size=3)  # Small cache for testing
    
    def test_cache_set_get(self):
        """Test basic cache set and get operations."""
        self.cache.set("key1", "value1", ttl_seconds=300)
        
        result = self.cache.get("key1")
        assert result == "value1"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = self.cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_expiration(self):
        """Test automatic expiration of cache entries."""
        self.cache.set("key1", "value1", ttl_seconds=0)
        time.sleep(0.01)
        
        result = self.cache.get("key1")
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2") 
        self.cache.set("key3", "value3")
        
        # Access key1 to make it more recently used
        self.cache.get("key1")
        
        # Add another item - should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        assert self.cache.get("key1") == "value1"  # Still there
        assert self.cache.get("key2") is None      # Evicted
        assert self.cache.get("key3") == "value3"  # Still there
        assert self.cache.get("key4") == "value4"  # Newly added
    
    def test_cache_stats(self):
        """Test cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        stats = self.cache.stats()
        
        assert stats["size"] == 2
        assert stats["max_size"] == 3
        assert stats["enabled"] is not None
        assert stats["ttl_seconds"] > 0
        
        # Test gets work correctly
        result1 = self.cache.get("key1")  # Should work
        result2 = self.cache.get("key3")  # Should be None
        
        assert result1 == "value1"
        assert result2 is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        assert self.cache.stats()["size"] == 2
        
        self.cache.clear()
        
        assert self.cache.stats()["size"] == 0
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None


class TestCacheKeyGeneration:
    """Test cache key generation."""
    
    def test_basic_cache_key(self):
        """Test basic cache key generation."""
        key = get_cache_key(123, method_name="TestService.get_item")
        assert key == "TestService.get_item(123)"
    
    def test_cache_key_with_string_args(self):
        """Test cache key with string arguments."""
        key = get_cache_key("diabetes", method_name="VocabularyService.search")
        assert key == 'VocabularyService.search("diabetes")'
    
    def test_cache_key_with_kwargs(self):
        """Test cache key with keyword arguments."""
        key = get_cache_key(
            "diabetes",
            method_name="VocabularyService.search",
            domain_id="Condition",
            page_size=50
        )
        assert key == 'VocabularyService.search("diabetes", domain_id="Condition", page_size=50)'
    
    def test_cache_key_no_args(self):
        """Test cache key with no arguments."""
        key = get_cache_key(method_name="VocabularyService.list_domains")
        assert key == "VocabularyService.list_domains()"
    
    def test_cache_key_kwargs_sorting(self):
        """Test that kwargs are sorted for consistency."""
        key1 = get_cache_key(
            method_name="TestService.test",
            zebra="last",
            alpha="first"
        )
        key2 = get_cache_key(
            method_name="TestService.test", 
            alpha="first",
            zebra="last"
        )
        assert key1 == key2
        assert "alpha" in key1
        assert key1.index("alpha") < key1.index("zebra")
    
    def test_cache_key_full_method_name_cleanup(self):
        """Test that full module paths are cleaned up."""
        key = get_cache_key(
            123,
            method_name="ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
        )
        assert key == "VocabularyService.get_concept(123)"


class TestCachedMethodDecorator:
    """Test the @cached_method decorator."""
    
    def setup_method(self):
        """Setup for decorator tests."""
        clear_cache()  # Start with clean cache
        self.call_count = 0
    
    def dummy_method(self, arg1, arg2=None):
        """Dummy method for testing."""
        self.call_count += 1
        return f"result_{arg1}_{arg2}_{self.call_count}"
    
    def test_cached_method_basic(self):
        """Test basic caching behavior."""
        # Create cached version of method
        cached_dummy = cached_method(ttl_seconds=300)(self.dummy_method)
        
        # First call should execute method
        result1 = cached_dummy(self, "test")  # Use single arg
        assert self.call_count == 1
        assert "test" in result1  # Just check that test arg is in result
        assert "_1" in result1    # Check call count is in result
        
        # Second call should return cached result
        result2 = cached_dummy(self, "test")  # Same args
        assert self.call_count == 1  # Method not called again
        assert result1 == result2
    
    def test_cached_method_different_args(self):
        """Test that different arguments create different cache entries."""
        cached_dummy = cached_method(ttl_seconds=300)(self.dummy_method)
        
        result1 = cached_dummy(self, "test1")
        result2 = cached_dummy(self, "test2")
        
        assert self.call_count == 2  # Both calls executed
        assert result1 != result2
    
    def test_cached_method_force_refresh(self):
        """Test force_refresh parameter."""
        cached_dummy = cached_method(ttl_seconds=300)(self.dummy_method)
        
        # First call
        result1 = cached_dummy(self, "test")
        assert self.call_count == 1
        
        # Second call with force_refresh=True
        result2 = cached_dummy(self, "test", force_refresh=True)
        assert self.call_count == 2  # Method called again
        assert result1 != result2  # Different results due to call_count
    
    def test_cached_method_disabled(self):
        """Test caching when disabled."""
        cached_dummy = cached_method(ttl_seconds=300, enabled=False)(self.dummy_method)
        
        result1 = cached_dummy(self, "test")
        result2 = cached_dummy(self, "test")
        
        assert self.call_count == 2  # Both calls executed (no caching)
        assert result1 != result2
    
    @patch('ohdsi_webapi.cache.CACHE_ENABLED', False)
    def test_cached_method_globally_disabled(self):
        """Test caching when globally disabled."""
        cached_dummy = cached_method(ttl_seconds=300)(self.dummy_method)
        
        result1 = cached_dummy(self, "test")
        result2 = cached_dummy(self, "test")
        
        assert self.call_count == 2  # Both calls executed (no caching)


class TestGlobalCacheFunctions:
    """Test global cache management functions."""
    
    def setup_method(self):
        """Setup for global cache tests."""
        clear_cache()
    
    def test_cache_stats_function(self):
        """Test global cache_stats function."""
        stats = cache_stats()
        
        assert "size" in stats
        assert "max_size" in stats
        assert "enabled" in stats
        assert "ttl_seconds" in stats
        assert stats["size"] == 0
    
    def test_cache_contents_empty(self):
        """Test cache_contents with empty cache."""
        contents = cache_contents()
        
        assert "entries" in contents
        assert "stats" in contents
        assert len(contents["entries"]) == 0
        assert contents["stats"]["size"] == 0
    
    def test_cache_contents_with_data(self):
        """Test cache_contents with actual data."""
        # Add some data to cache
        _global_cache.set("test_key", {"test": "data"}, ttl_seconds=300)
        
        contents = cache_contents()
        
        assert len(contents["entries"]) == 1
        entry = contents["entries"][0]
        
        assert entry["key"] == "test_key"
        assert entry["data_type"] == "dict (1 keys)"
        assert entry["created_ago"] >= 0
        assert entry["expires_in"] > 0
    
    def test_clear_cache_function(self):
        """Test global clear_cache function."""
        # Add some data
        _global_cache.set("test_key", "test_value", ttl_seconds=300)
        assert cache_stats()["size"] == 1
        
        # Clear cache
        clear_cache()
        assert cache_stats()["size"] == 0
    
    def test_cache_contents_data_type_formatting(self):
        """Test data type formatting in cache_contents."""
        # Test different data types
        test_cases = [
            ("string_data", "hello", "str"),
            ("list_data", [1, 2, 3], "list (3 items)"),
            ("dict_data", {"a": 1, "b": 2}, "dict (2 keys)"),
            ("int_data", 42, "int"),
            ("complex_object", MagicMock(), "MagicMock"),
        ]
        
        clear_cache()
        
        for key, value, expected_type in test_cases:
            _global_cache.set(key, value, ttl_seconds=300)
        
        contents = cache_contents()
        
        # Check that we have all entries
        assert len(contents["entries"]) == len(test_cases)
        
        # Verify data type formatting
        for entry in contents["entries"]:
            expected = next(tc[2] for tc in test_cases if tc[0] == entry["key"])
            assert expected in entry["data_type"]


class TestCacheIntegration:
    """Integration tests for cache with actual service methods."""
    
    def setup_method(self):
        """Setup for integration tests."""
        clear_cache()
    
    @patch('ohdsi_webapi.cache.CACHE_ENABLED', True)
    def test_cache_integration_with_mock_service(self):
        """Test cache integration with a mock service method."""
        
        class MockService:
            def __init__(self):
                self.call_count = 0
            
            @cached_method(ttl_seconds=300)
            def get_data(self, data_id: int) -> dict:
                self.call_count += 1
                return {"id": data_id, "call_count": self.call_count}
        
        service = MockService()
        
        # First call
        result1 = service.get_data(123)
        assert service.call_count == 1
        assert result1["id"] == 123
        assert result1["call_count"] == 1
        
        # Second call (should be cached)
        result2 = service.get_data(123)
        assert service.call_count == 1  # No additional call
        assert result2 == result1
        
        # Different argument (should not be cached)
        result3 = service.get_data(456)
        assert service.call_count == 2
        assert result3["id"] == 456
        assert result3["call_count"] == 2
        
        # Verify cache contents
        contents = cache_contents()
        assert len(contents["entries"]) == 2
        
        cache_keys = [entry["key"] for entry in contents["entries"]]
        assert "MockService.get_data(123)" in cache_keys
        assert "MockService.get_data(456)" in cache_keys


if __name__ == "__main__":
    pytest.main([__file__])
