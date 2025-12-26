# Kibana Visualizations Import Guide

## Visualizations Included

1. **logs_per_hour_viz.ndjson** - Line chart showing total logs and errors per hour
2. **top_error_messages_viz.ndjson** - Horizontal bar chart of most frequent error messages by service
3. **transaction_amount_distribution_viz.ndjson** - Donut chart showing transaction amount ranges

## Prerequisites

- Kibana must be running (default: http://localhost:5601)
- Index pattern `logs-ecom-*` must exist
- Logs must contain the following fields:
  - `@timestamp` (date)
  - `level` (keyword)
  - `message` (text with .keyword subfield)
  - `service` (text with .keyword subfield)
  - `transaction_amount` (numeric, for payment service logs)

## Import Instructions

### Method 1: Via Kibana UI (Recommended)

1. **Access Kibana**
   - Open your browser and navigate to: http://localhost:5601

2. **Open Stack Management**
   - Click the hamburger menu (☰) in the top-left
   - Scroll down to **Management** section
   - Click **Stack Management**

3. **Navigate to Saved Objects**
   - In the left sidebar, under **Kibana** section
   - Click **Saved Objects**

4. **Import Visualizations**
   - Click the **Import** button (top-right corner)
   - Click **Import** again in the dialog
   - Select one of the `.ndjson` files:
     - `logs_per_hour_viz.ndjson`
     - `top_error_messages_viz.ndjson`
     - `transaction_amount_distribution_viz.ndjson`
   - Click **Open**

5. **Resolve Conflicts (if any)**
   - If prompted about existing objects, choose:
     - **Automatically overwrite conflicts** (to replace existing)
     - **Request action on each conflict** (to review individually)
   - Click **Import**

6. **Verify Import**
   - You should see: "Successfully imported X objects"
   - Click **Done**

7. **Repeat for Other Visualizations**
   - Repeat steps 4-6 for each `.ndjson` file

### Method 2: Via cURL (Advanced)

```bash
# Import logs per hour visualization
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@kibana_exports/logs_per_hour_viz.ndjson

# Import top error messages visualization
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@kibana_exports/top_error_messages_viz.ndjson

# Import transaction amount distribution
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@kibana_exports/transaction_amount_distribution_viz.ndjson
```

### Method 3: PowerShell (Windows)

```powershell
# Navigate to project directory
cd C:\projet_bigdata

# Import each visualization
$files = @(
    "kibana_exports\logs_per_hour_viz.ndjson",
    "kibana_exports\top_error_messages_viz.ndjson",
    "kibana_exports\transaction_amount_distribution_viz.ndjson"
)

foreach ($file in $files) {
    $uri = "http://localhost:5601/api/saved_objects/_import"
    $headers = @{ "kbn-xsrf" = "true" }
    
    # Create multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBinary = [System.IO.File]::ReadAllBytes($file)
    $fileName = Split-Path $file -Leaf
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: application/ndjson",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileBinary),
        "--$boundary--"
    ) -join "`r`n"
    
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers `
        -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyLines
    
    Write-Host "Imported: $fileName - Success: $($response.success)"
}
```

## View Imported Visualizations

### Option 1: From Visualize Library

1. Click hamburger menu (☰) → **Visualize Library**
2. You should see three new visualizations:
   - Logs per Hour - E-commerce
   - Top Error Messages - E-commerce
   - Transaction Amount Distribution - E-commerce
3. Click on any visualization to view it

### Option 2: Create a Dashboard

1. Click hamburger menu (☰) → **Dashboard**
2. Click **Create dashboard**
3. Click **Add from library**
4. Search for "E-commerce"
5. Select all three visualizations
6. Click **Add to dashboard**
7. Arrange and resize as desired
8. Click **Save** and name it "E-commerce Logs Dashboard"

## Customization

### Time Range

- Use the time picker (top-right) to change the time range:
  - Last 15 minutes
  - Last 24 hours
  - Last 7 days
  - Custom range

### Filters

- Add filters in the search bar at the top:
  ```
  service:payment
  level:ERROR
  transaction_amount > 100
  ```

### Edit Visualizations

1. Open the visualization
2. Click **Edit** (top-right)
3. Modify:
   - **Data** tab: Change metrics, aggregations, field
   - **Options** tab: Customize colors, labels, legends
4. Click **Save**

## Troubleshooting

### "Index pattern not found" Error

**Solution:**
1. Go to **Stack Management** → **Index Patterns**
2. Click **Create index pattern**
3. Enter pattern: `logs-ecom-*`
4. Select `@timestamp` as time field
5. Click **Create**
6. Re-import the visualizations

### "Field not found" Error

**Solution:**
- Ensure your logs contain the required fields
- Refresh the field list:
  1. Stack Management → Index Patterns
  2. Select `logs-ecom-*`
  3. Click **Refresh field list** (top-right)

### Visualizations Show No Data

**Solution:**
1. Check time range (expand to "Last 30 days")
2. Verify logs exist in Elasticsearch:
   ```bash
   curl -X GET "http://localhost:9200/logs-ecom-*/_count"
   ```
3. Check field mappings match your data structure

### Import Fails with "Conflict" Error

**Solution:**
- Choose **Automatically overwrite conflicts** during import
- Or delete existing visualizations first:
  1. Stack Management → Saved Objects
  2. Search for "E-commerce"
  3. Select and delete existing visualizations
  4. Re-import

## Field Requirements

### Required for All Visualizations
- `@timestamp` (date)
- `level` (keyword)
- `service` (keyword)

### Required for Top Error Messages
- `message` (text) with `message.keyword` (keyword) subfield

### Required for Transaction Amount Distribution
- `transaction_amount` (long or double)
- Only logs from `service:payment` with valid amounts

## Next Steps

1. **Create an Index Lifecycle Policy** to manage old log indices
2. **Set up Alerts** based on error thresholds
3. **Create additional visualizations**:
   - Logs by service (pie chart)
   - Error rate over time (area chart)
   - Top users by activity (data table)
4. **Build a comprehensive dashboard** combining all visualizations

## Support

For issues or questions, refer to:
- Kibana Documentation: https://www.elastic.co/guide/en/kibana/current/index.html
- Project README: c:\projet_bigdata\README.md
