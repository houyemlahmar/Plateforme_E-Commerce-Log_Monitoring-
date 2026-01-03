# Running the Application - Quick Guide

## Problem: Service Connection Errors

If you see errors like:
```
mongodb:27017: [Errno 11001] getaddrinfo failed
Failed to resolve 'elasticsearch'
```

This means the application can't connect to required services.

## Solution Options

### Option 1: Start Services with Docker Compose (Recommended)

This starts all required services (MongoDB, Elasticsearch, etc.):

```bash
# From the project root
cd C:\projet_bigdata

# Start all services
docker-compose up -d

# Or start only MongoDB (minimum requirement)
docker-compose up -d mongodb

# Check services are running
docker-compose ps

# Then run Flask app
cd backend
python main.py
```

### Option 2: Run MongoDB Locally

If you don't want to use Docker:

1. **Install MongoDB:**
   - Download from: https://www.mongodb.com/try/download/community
   - Install MongoDB Community Edition
   - Start MongoDB service

2. **Verify MongoDB is running:**
   ```bash
   # Check if port 27017 is open
   netstat -an | findstr :27017
   ```

3. **Run Flask app:**
   ```bash
   cd C:\projet_bigdata\backend
   python check_services.py  # Check if services are ready
   python main.py
   ```

## Quick Service Check

Before starting the Flask app, check if services are running:

```bash
cd C:\projet_bigdata\backend
python check_services.py
```

This will show:
- ✓ MongoDB: Required for authentication
- ✓ Elasticsearch: Optional (for log search)
- ✓ Redis: Optional (for caching)

## Testing Authentication Without Other Services

The JWT authentication system only **requires MongoDB**. You can test authentication even if Elasticsearch and Redis are not running:

```bash
# 1. Start MongoDB
cd C:\projet_bigdata
docker-compose up -d mongodb

# 2. Check services
cd backend
python check_services.py

# 3. Create admin user
python init_admin.py

# 4. Start Flask app (will skip Elasticsearch/Redis if not available)
python main.py

# 5. Test authentication (in another terminal)
python test_auth.py
```

## Service Requirements

| Service | Port | Required For | Can Skip? |
|---------|------|--------------|-----------|
| MongoDB | 27017 | Authentication, user storage | ❌ No |
| Elasticsearch | 9200 | Log search and analytics | ✅ Yes |
| Redis | 6379 | Caching | ✅ Yes |
| Kibana | 5601 | Visualization | ✅ Yes |
| Logstash | 5000 | Log ingestion | ✅ Yes |

## Docker Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d mongodb

# Stop all services
docker-compose down

# View logs
docker-compose logs -f mongodb

# Check service status
docker-compose ps

# Restart service
docker-compose restart mongodb
```

## Environment Configuration

The `.env` file in `backend/` folder is configured for local development:
- MongoDB: `localhost:27017`
- Elasticsearch: `localhost:9200`
- Redis: `localhost:6379`

When running inside Docker, these automatically change to service names.

## Troubleshooting

### Error: "getaddrinfo failed"
**Cause:** Service not running or wrong hostname
**Fix:** Start service with `docker-compose up -d mongodb`

### Error: "Connection refused"
**Cause:** Service not started yet or port blocked
**Fix:** Wait a few seconds for service to start, or check firewall

### Error: "No module named 'colorama'"
**Fix:** `pip install colorama`

### MongoDB Won't Start
```bash
# Check if port is already in use
netstat -an | findstr :27017

# Stop existing MongoDB
docker-compose down mongodb

# Remove old volumes and restart
docker-compose down -v
docker-compose up -d mongodb
```

## Quick Start (Step-by-Step)

```bash
# 1. Navigate to project
cd C:\projet_bigdata

# 2. Start MongoDB
docker-compose up -d mongodb

# Wait 5-10 seconds for MongoDB to start

# 3. Check services
cd backend
python check_services.py

# 4. Create admin user (first time only)
python init_admin.py

# 5. Start Flask app
python main.py

# 6. In another terminal, test authentication
cd C:\projet_bigdata\backend
python test_auth.py
```

## Success Indicators

When everything is working:
```
✓ MongoDB is running on localhost:27017
✓ Extensions initialized successfully
✓ Flask application started on 0.0.0.0:5000
```

## Additional Help

- **Check services script:** `python check_services.py`
- **Authentication docs:** See `JWT_AUTHENTICATION.md`
- **Quick start guide:** See `AUTH_QUICKSTART.md`
