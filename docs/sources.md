# Sources in OHDSI WebAPI

## What are (Data) Sources?

A **data source** in OHDSI represents a specific database containing healthcare data that has been converted to the [OMOP Common Data Model (CDM)](https://ohdsi.github.io/CommonDataModel/) format. Think of it as a pointer to a particular healthcare dataset that OHDSI tools can analyze.

Examples of data sources might include:
- A hospital's electronic health records (EHR) 
- Medicare claims data
- Clinical trial datasets
- Research databases like Optum or Truven

## How Sources are Configured

When OHDSI WebAPI is installed, administrators configure one or more data sources in the WebAPI database. Each source represents a different healthcare database that researchers can query.

### Source Configuration Fields

Each data source has these key properties:

| JSON Field | Python Attribute | Description | Example |
|------------|------------------|-------------|---------|
| `sourceId` | `source_id` | Numeric database ID (primary key) | `1` |
| `sourceKey` | `source_key` | Short string identifier used in API calls | `"SYNPUF"` |
| `sourceName` | `source_name` | Human-readable description | `"CMS Synthetic Public Use Files"` |
| `cdmSchema` | N/A | Database schema containing the OMOP CDM tables | `"cdm_synpuf"` |
| `resultsSchema` | N/A | Schema where analysis results are stored | `"results_synpuf"` |
| Connection details | N/A | Database connection info (JDBC URL, credentials, etc.) | `"jdbc:postgresql://..."` |

### Example Source Configuration

```
| source_id | source_key | source_name                   | cdm_schema  | results_schema |
|-----------|------------|-------------------------------|-------------|----------------|
| 1         | SYNPUF     | CMS Synthetic Public Use      | cdm_synpuf  | results_synpuf |
| 2         | EHR_UK     | UK EHR OMOP Conversion        | omop_ehr    | results_ehr    |
| 3         | OPTUM      | Optum Clinformatics Data Mart | cdm_optum   | results_optum  |
```

## Working with Sources in Your Code

### 1. List Available Sources

First, discover what data sources are available:

```python
from ohdsi_webapi import WebApiClient

client = WebApiClient("https://your-webapi-url.com")

# Get list of all configured sources
sources = client.sources.list()

for source in sources:
    print(f"Key: {source.source_key}, Name: {source.source_name}")
```

### 2. Understanding source_key

The `source_key` is like a nickname for each database. Instead of dealing with complex connection strings, you just use the short key (like `"SYNPUF"` or `"EHR_UK"`) in your API calls.

This key tells WebAPI:
- Which database to connect to
- What SQL dialect to use (PostgreSQL, SQL Server, etc.)
- Where to find the OMOP tables
- Where to store analysis results

## Running Cohort Definitions Against Sources

When you want to identify patients who meet certain criteria (a "cohort"), you specify which data source to search:

### Step-by-Step Process

```python
# 1. Create a cohort definition
cohort_def = {
    "name": "Diabetes Patients",
    "expression": {
        # Your cohort criteria here...
    }
}

# 2. Save the definition to WebAPI
saved_cohort = client.create_cohort_definition(cohort_def)
cohort_id = saved_cohort.id

# 3. Generate the cohort against a specific data source
client.generate_cohort(
    cohort_definition_id=cohort_id,
    source_key="SYNPUF"  # Use the source_key here
)

# 4. Check generation status and get results
status = client.get_generation_status(cohort_id, "SYNPUF")
if status.is_complete:
    results = client.get_cohort_results(cohort_id, "SYNPUF")
```

### What Happens Behind the Scenes

When you call `generate_cohort(cohort_id, "SYNPUF")`, WebAPI:

1. **Looks up the source**: Finds the database connection details for `"SYNPUF"`
2. **Resolves concepts**: Translates your medical concepts (like "diabetes") into specific codes for that database
3. **Generates SQL**: Uses the Circe engine to create optimized SQL for that database's dialect
4. **Executes the query**: Runs the SQL against the CDM schema (`cdm_synpuf`)
5. **Stores results**: Saves the patient cohort in the results schema (`results_synpuf`)

## Why Multiple Sources Matter

Different data sources have different characteristics:

- **Population coverage**: Medicare vs. commercial insurance vs. international
- **Time periods**: Historical data from 2010-2015 vs. recent data from 2020-2025  
- **Data quality**: Some sources have more complete lab values, others better prescription data
- **Size**: Millions of patients vs. thousands

By running the same cohort definition against multiple sources, researchers can:
- **Validate findings**: Do results replicate across different populations?
- **Increase sample size**: Combine results from multiple databases
- **Study population differences**: How do outcomes vary by geography or insurance type?

## Best Practices

### Choosing the Right Source

```python
# Get source details to understand what you're working with
sources = client.sources.list()

for source in sources:
    info = client.get_source_info(source.source_key)
    print(f"""
    Source: {source.source_name}
    Patients: {info.person_count:,}
    Data Range: {info.min_observation_date} to {info.max_observation_date}
    """)
```

### Error Handling

```python
try:
    client.generate_cohort(cohort_id, "SYNPUF")
except SourceNotFoundError:
    print("Source 'SYNPUF' is not configured or accessible")
except GenerationError as e:
    print(f"Cohort generation failed: {e.message}")
```

### Checking Source Availability

```python
# Verify a source exists before using it
available_keys = [s.source_key for s in client.sources.list()]

if "SYNPUF" in available_keys:
    # Safe to use this source
    client.generate_cohort(cohort_id, "SYNPUF")
else:
    print("SYNPUF source not available")
```

## Common Questions

**Q: How do I know which source to use for my research?**  
A: It depends on your research question. Use `client.sources.list()` and `get_source_info()` to understand the characteristics of each available source.

**Q: Can I run the same cohort on multiple sources?**  
A: Yes! This is common for validation studies. Just call `generate_cohort()` with different `source_key` values.

**Q: What if a source is unavailable or down?**  
A: The API will return an error. Always handle exceptions and have fallback logic for critical applications.

**Q: Who configures these sources?**  
A: The WebAPI administrator sets up sources during installation. As a developer, you consume the pre-configured sources via the API.
