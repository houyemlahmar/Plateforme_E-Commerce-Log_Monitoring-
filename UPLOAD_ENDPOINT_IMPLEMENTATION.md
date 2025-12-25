# POST /upload Implementation Summary

## ✅ What Has Been Implemented

### 1. Route: POST /api/logs/upload
**Location**: `backend/app/routes/logs_routes.py`

**Features**:
- ✅ File validation (size, extension: CSV/JSON only)
- ✅ Save file to `/uploads` directory with unique filename
- ✅ Extract first 10 lines for preview
- ✅ Insert metadata into MongoDB collection "uploads"
- ✅ Push job ID into Redis queue "ingest_jobs"
- ✅ Clean JSON responses with structured data
- ✅ Comprehensive exception handling (ValueError, IOError, general Exception)

**Response Format**:
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "file_id": "MongoDB ObjectId",
    "job_id": "UUID v4",
    "filename": "original_filename.csv",
    "file_size": 1234,
    "file_type": "csv",
    "preview": [...],
    "preview_lines": 10,
    "total_lines": 100,
    "uploaded_at": "2025-12-25T10:00:00"
  }
}
```

### 2. Service Method: `process_upload_with_preview()`
**Location**: `backend/app/services/log_service.py`

**Functionality**:
- Generates unique job ID (UUID)
- Creates `uploads/` directory if not exists
- Saves file with timestamped unique name: `YYYYMMDD_HHMMSS_{job_id[:8]}_{filename}`
- Extracts first 10 lines for preview
- Parses preview based on file type:
  - **JSON**: Parses each line as JSON object
  - **CSV**: Uses DictReader for structured parsing
- Stores metadata in MongoDB "uploads" collection with fields:
  - `job_id`, `filename`, `unique_filename`, `file_path`
  - `file_size`, `file_type`, `total_lines`
  - `preview`, `uploaded_at`, `status`, `processed`
- Pushes job to Redis list "ingest_jobs" with JSON serialized data
- Returns comprehensive upload result

### 3. Enhanced Validator
**Location**: `backend/app/utils/validators.py`

**Updates**:
- Added `allowed_extensions` parameter (defaults to config, can be overridden)
- Strict validation for CSV/JSON only when called from `/upload` route
- File size displayed in MB for better readability
- More descriptive error messages

### 4. Redis Service Queue Methods
**Location**: `backend/app/services/redis_service.py`

**New Methods**:
- `lpush(key, *values)` - Push to list head
- `rpush(key, *values)` - Push to list tail
- `lpop(key)` - Pop from list head with JSON deserialization
- `rpop(key)` - Pop from list tail with JSON deserialization
- `llen(key)` - Get list length
- `lrange(key, start, end)` - Get list range

### 5. Celery Tasks
**Location**: `backend/app/tasks/log_tasks.py`

**Tasks Created**:
- `process_ingest_job(job_data)` - Process individual upload job
- `process_ingest_queue()` - Batch process all jobs in "ingest_jobs" queue

### 6. Test Script
**Location**: `test_upload_endpoint.py`

**Tests**:
1. Upload JSON file (12 lines) - expects 201
2. Upload CSV file (11 lines) - expects 201
3. Upload .txt file (invalid extension) - expects 400
4. Upload empty file - expects 400
5. Upload without file - expects 400

## 📋 Configuration

### Config File: `backend/config.py`
Already configured:
```python
MAX_UPLOAD_SIZE = 104857600  # 100MB
ALLOWED_LOG_EXTENSIONS = ['log', 'txt', 'json', 'csv']
```

### MongoDB Collection: "uploads"
Schema:
```python
{
    'job_id': str,           # UUID v4
    'filename': str,         # Original filename
    'unique_filename': str,  # Timestamped unique filename
    'file_path': str,        # Full path to saved file
    'file_size': int,        # Size in bytes
    'file_type': str,        # 'csv' or 'json'
    'total_lines': int,      # Total lines in file
    'preview': list,         # First 10 lines parsed
    'uploaded_at': datetime, # Upload timestamp
    'status': str,           # 'pending', 'processing', 'completed', 'failed'
    'processed': bool        # Processing status flag
}
```

### Redis Queue: "ingest_jobs"
Format:
```python
{
    'job_id': str,
    'file_id': str,
    'file_path': str,
    'file_type': str,
    'total_lines': int,
    'created_at': str  # ISO format
}
```

## 🧪 Testing

### Run Tests
```powershell
# Make sure Flask is running
docker-compose ps

# Install requests if needed
pip install requests

# Run test script
python test_upload_endpoint.py
```

### Manual Test with cURL
```powershell
# Upload JSON file
curl -X POST http://localhost:5001/api/logs/upload `
  -F "file=@uploads/test_logs.json"

# Upload CSV file
curl -X POST http://localhost:5001/api/logs/upload `
  -F "file=@uploads/test_csv.csv"
```

### Check Results

**MongoDB**:
```powershell
docker-compose exec mongodb mongosh -u admin -p mongodb_password --eval "use ecommerce_logs; db.uploads.find().pretty()"
```

**Redis Queue**:
```powershell
docker-compose exec redis redis-cli -a redis_password LLEN ingest_jobs
docker-compose exec redis redis-cli -a redis_password LRANGE ingest_jobs 0 -1
```

**Uploaded Files**:
```powershell
Get-ChildItem uploads\
```

## 🔄 Processing Flow

```
1. Client uploads file → POST /api/logs/upload
2. Route validates file (size, extension)
3. LogService.process_upload_with_preview():
   - Saves file to /uploads
   - Extracts 10-line preview
   - Inserts metadata → MongoDB "uploads" collection
   - Pushes job → Redis "ingest_jobs" queue
4. Returns response with file_id, job_id, preview
5. Celery worker (optional) processes jobs from queue
```

## 📝 Notes

- All exceptions properly handled with clean JSON responses
- File size validation: 100MB max (configurable)
- Only CSV and JSON extensions allowed
- Preview parsing handles malformed data gracefully
- Job ID uses UUID v4 for uniqueness
- Files saved with timestamp prefix to prevent collisions
- MongoDB stores complete metadata for tracking
- Redis queue enables async processing with Celery
