# Caching

The OHDSI WebAPI client includes intelligent caching to improve performance, especially for expensive operations like listing all concept sets (20,000+ items) or frequently accessed concepts.

## Configuration

Caching is controlled by environment variables:

```bash
# Enable/disable caching (default: true)
export OHDSI_CACHE_ENABLED=true

# Cache TTL in seconds (default: 300 = 5 minutes)
export OHDSI_CACHE_TTL=600

# Maximum cache entries (default: 128)
export OHDSI_CACHE_MAX_SIZE=256
```

## Cache Keys

The caching system generates **human-readable cache keys** that make debugging and monitoring easy:

```python
# Method call
client.vocabulary.concept(201826)
# Generated cache key: "VocabularyService.concept(201826)"

# Search with parameters  
client.vocabulary.search("diabetes", domain_id="Condition", page_size=50)
# Generated cache key: "VocabularyService.search("diabetes", domain_id="Condition", page_size=50)"
```

### Key Generation Process

1. **Method name**: Uses clean service and method name (e.g., `VocabularyService.concept`)
2. **Arguments**: All positional arguments included (excluding `self`)
3. **Keyword arguments**: Sorted alphabetically for consistency
4. **Special parameters**: `force_refresh` is excluded from cache keys

## Automatic Caching

The following methods are automatically cached:

### High-Value Targets
- `client.conceptset()` - 1 hour cache (expensive: 20K+ items)
- `client.conceptset(id)` - 30 minute cache (stable individual sets)
- `client.conceptset_items(id)` - 30 minute cache (resolved concept lists)
- `client.vocabulary.concept(id)` - 1 hour cache (concepts rarely change)
- `client.vocabulary.domains()` - 30 minute cache (stable metadata)

### Performance Impact
```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# First call: hits API (~10 seconds for 27K concept sets)
concept_sets = client.conceptset()

# Subsequent calls: instant (from cache for 1 hour)
concept_sets = client.conceptset() # much faster
```

## Force Refresh

Bypass the cache for any method by adding `force_refresh=True`:

```python
# Normal cached call
concept = client.vocabulary.concept(201826)

# Force fresh data from server (bypasses cache)
fresh_concept = client.vocabulary.concept(201826, force_refresh=True)
```

### How force_refresh Works

When `force_refresh=True` is passed to a cached method:

1. **Parameter extraction**: `force_refresh` is removed from kwargs before cache key generation
2. **Complete bypass**: The decorator skips all cache logic (no read, no write)
3. **Direct API call**: The original method is called directly to fetch fresh data
4. **Cache preservation**: Existing cache entries remain unchanged

**Important**: `force_refresh=True` completely bypasses the cache - it neither reads from nor writes to the cache for that specific call.

## Cache Management

```python
# Check cache status
stats = client.cache_stats()
print(f"Cached items: {stats['size']}/{stats['max_size']}")
print(f"TTL: {stats['ttl_seconds']} seconds")

# Clear all cached data
client.clear_cache()
```

## Cache Behavior

### TTL (Time-to-Live)
- Entries automatically expire based on `OHDSI_CACHE_TTL`
- Different methods have optimized TTLs based on data stability
- Expired entries are cleaned up automatically

### LRU Eviction
- When cache is full, least recently used items are removed
- Cache size controlled by `OHDSI_CACHE_MAX_SIZE`

### Memory Efficient
- In-memory cache only (no disk storage)
- Automatic cleanup of expired entries
- Reasonable defaults prevent memory bloat

## Production Recommendations

### Long-Running Applications
```bash
# Longer TTL for stable production data
export OHDSI_CACHE_TTL=3600  # 1 hour

# Larger cache for high-volume apps
export OHDSI_CACHE_MAX_SIZE=512
```

### Development/Testing
```bash
# Shorter TTL to see changes quickly
export OHDSI_CACHE_TTL=60  # 1 minute

# Disable caching for debugging
export OHDSI_CACHE_ENABLED=false
```


## Troubleshooting

### Disable Caching
```bash
export OHDSI_CACHE_ENABLED=false
```

### Debug Cache Behavior
```python
print("Before:", client.cache_stats())
result = client.conceptset()
print("After:", client.cache_stats())
```

### Memory Usage
The cache uses modest memory:
- Concept metadata: ~1KB per concept
- Concept set list (27K items): ~5MB
- Individual concept sets: varies by expression size

With default settings (128 items, 5 min TTL), memory usage typically stays under 50MB.
