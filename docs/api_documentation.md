# API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API is open for development. In production, use JWT tokens:

```http
Authorization: Bearer <token>
```

## Endpoints

### Health Check

#### GET /health

Check if the application is running.

**Response**

```json
{
  "status": "healthy",
  "service": "ecommerce-logs-platform",
  "version": "1.0.0"
}
```

---

### Logs Management

#### POST /logs/upload

Upload a log file.

**Request**

- Content-Type: `multipart/form-data`
- Body: `file` (log file)

**Response**

```json
{
  "message": "Logs uploaded successfully",
  "records_processed": 1000,
  "file_id": "507f1f77bcf86cd799439011"
}
```

#### POST /logs/ingest

Ingest logs via JSON payload.

**Request**

```json
{
  "message": "Transaction completed",
  "log_type": "transaction",
  "transaction_id": "TXN12345",
  "user_id": "USER123",
  "amount": 99.99,
  "currency": "USD"
}
```

**Response**

```json
{
  "message": "Logs ingested successfully",
  "records_processed": 1
}
```

#### GET /logs/types

Get available log types.

**Response**

```json
{
  "log_types": [
    {
      "id": "transaction",
      "name": "Transaction Logs",
      "description": "Payment, order, and refund logs"
    },
    ...
  ]
}
```

#### GET /logs/recent

Get recent logs.

**Query Parameters**

- `limit` (optional): Number of logs (default: 100)
- `log_type` (optional): Filter by type

**Response**

```json
{
  "logs": [...],
  "count": 100
}
```

#### GET /logs/stats

Get logs statistics.

**Response**

```json
{
  "total_files": 50,
  "log_types": [
    {"type": "transaction", "count": 1000},
    {"type": "error", "count": 50}
  ],
  "timeline": [...]
}
```

---

### Analytics

#### GET /analytics/transactions

Get transaction analytics.

**Query Parameters**

- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `granularity` (optional): hourly, daily, weekly, monthly

**Response**

```json
{
  "timeline": [...],
  "payment_methods": [...],
  "transaction_status": [...]
}
```

#### GET /analytics/errors

Get error analytics.

**Response**

```json
{
  "error_codes": [...],
  "error_types": [...],
  "timeline": [...]
}
```

#### GET /analytics/user-behavior

Get user behavior analytics.

**Response**

```json
{
  "actions": [...],
  "pages": [...],
  "cart_abandonment_count": 150
}
```

#### GET /analytics/trends

Get trends analysis.

**Query Parameters**

- `time_range` (optional): 7d, 30d, etc. (default: 7d)

**Response**

```json
{
  "time_range": "7d",
  "log_types": [...]
}
```

---

### Dashboard

#### GET /dashboard/overview

Get dashboard overview.

**Response**

```json
{
  "total_logs_24h": 10000,
  "errors_24h": 150,
  "transactions_24h": 5000,
  "transaction_amount_24h": 250000.00,
  "fraud_alerts_24h": 5,
  "log_types_distribution": [...]
}
```

#### GET /dashboard/metrics

Get key metrics.

**Response**

```json
{
  "realtime": 1000,
  "last_24h": 10000,
  "last_7d": 50000,
  "error_rate": 1.5,
  "avg_response_time": 150.5
}
```

#### GET /dashboard/charts

Get chart data.

**Query Parameters**

- `chart_type`: transactions, errors, performance

**Response**

```json
{
  "labels": [...],
  "data": [...]
}
```

---

### Fraud Detection

#### POST /fraud/detect

Detect fraud in transaction data.

**Request**

```json
{
  "transaction_id": "TXN12345",
  "user_id": "USER123",
  "amount": 15000.00,
  "currency": "USD",
  "payment_method": "credit_card",
  "location": "XX"
}
```

**Response**

```json
{
  "is_fraud": true,
  "fraud_score": 85,
  "indicators": ["high_amount", "suspicious_location"],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /fraud/suspicious-activities

Get suspicious activities.

**Query Parameters**

- `limit` (optional): Number of activities (default: 100)

**Response**

```json
{
  "activities": [...],
  "count": 25
}
```

#### GET /fraud/stats

Get fraud statistics.

**Response**

```json
{
  "total_fraud_detected_24h": 10,
  "avg_fraud_score": 65.5,
  "top_indicators": [...]
}
```

---

### Performance

#### GET /performance/metrics

Get performance metrics.

**Response**

```json
{
  "avg_response_time": 150.5,
  "max_response_time": 2500.0,
  "min_response_time": 10.0,
  "percentiles": {...},
  "by_endpoint": [...]
}
```

#### GET /performance/api-response-times

Get API response times.

**Response**

```json
{
  "timeline": [...],
  "by_api": [...]
}
```

#### GET /performance/database-latency

Get database latency.

**Response**

```json
{
  "avg_db_latency": 50.5,
  "max_db_latency": 500.0,
  "slow_queries_count": 10,
  "by_query_type": [...]
}
```

---

### Search

#### GET /search/

Search logs.

**Query Parameters**

- `q`: Search query
- `log_type` (optional): Filter by type
- `from` (optional): Start date
- `to` (optional): End date
- `size` (optional): Number of results (default: 100)

**Response**

```json
{
  "total": 1000,
  "results": [...],
  "query": "error",
  "filters": {...}
}
```

#### GET /search/autocomplete

Get autocomplete suggestions.

**Query Parameters**

- `q`: Partial query

**Response**

```json
{
  "suggestions": ["transaction", "transfer", "transmit"]
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message description"
}
```

### Status Codes

- `200` : Success
- `201` : Created
- `400` : Bad Request
- `404` : Not Found
- `500` : Internal Server Error
