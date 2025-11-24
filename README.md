# AI Time Entry Rewrite - Production Setup Guide

A production-ready FastAPI application for rewriting legal time entry narratives using LLM (Ollama) with client-specific billing guidelines.

## Features

- ✅ PDF upload for client billing guidelines
- ✅ Automated text extraction from PDFs
- ✅ Client-specific rewrite rules
- ✅ Admin audit trail
- ✅ JWT authentication
- ✅ Environment-based configuration
- ✅ File upload validation (size limits, type checking)
- ✅ Input sanitization and validation
- ✅ CORS security
- ✅ Structured logging (JSON/colored output)
- ✅ Request/response logging
- ✅ Health check endpoints
- ✅ Error tracking and reporting
- ✅ Unit test suite

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- Ollama model: `qwen2.5:7b` (or configure your preferred model)

## Quick Start (Development)

### 1. Clone and Navigate

```bash
cd /path/to/a091dma
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env and update SECRET_KEY with the generated value
```

### 5. Start Ollama

```bash
# Make sure Ollama is running
ollama serve

# Pull the required model (in another terminal)
ollama pull qwen2.5:7b
```

### 6. Run the Application

```bash
uvicorn main:app --reload --port 9001
```

### 7. Access the Application

- **Frontend**: http://localhost:9001/index.html
- **API Docs**: http://localhost:9001/docs
- **Health Check**: http://localhost:9001/health

### 8. Default Credentials

- **Admin**: `admin` / `Admin123`
- **User**: `demo` / `Demo1234`

⚠️ **IMPORTANT**: Change these passwords immediately in production!

**Note**: Passwords must contain at least 8 characters with uppercase, lowercase, and numbers.

## Production Deployment

### Environment Configuration

Create a `.env` file with production values:

```bash
# Security - CRITICAL: Use a strong secret key
SECRET_KEY="your-super-secret-key-here-use-openssl-rand-base64-32"

# CORS - Only allow your production domains
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"

# Database - Use PostgreSQL for production
DATABASE_URL="postgresql://user:password@localhost:5432/time_rewrite"

# LLM Configuration
OLLAMA_URL="http://ollama-server:11434/api/generate"
MODEL_NAME="qwen2.5:7b"

# File Upload Limits
MAX_UPLOAD_SIZE=10485760  # 10MB

# Disable debug mode
DEBUG=false
```

### Security Checklist

- [ ] Generate a strong `SECRET_KEY` (minimum 32 characters)
- [ ] Configure `CORS_ORIGINS` to only allow your domains
- [ ] Change default admin password
- [ ] Use HTTPS/SSL in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=false`
- [ ] Review file upload size limits
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### Password Requirements

New passwords must meet these requirements:
- Minimum 8 characters (configurable via `MIN_PASSWORD_LENGTH`)
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### File Upload Security

- Maximum file size: 10MB (configurable via `MAX_UPLOAD_SIZE`)
- Allowed file types: PDF only
- Path traversal protection
- Encrypted PDF detection
- Empty file detection

### CORS Configuration

By default, CORS allows:
- `http://localhost:3000`
- `http://localhost:9001`
- `http://127.0.0.1:9001`

For production, update `CORS_ORIGINS` in `.env`:

```bash
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/token` - Get JWT token

### Clients
- `GET /clients/` - List all clients
- `GET /clients/{id}` - Get client details

### Rewrites
- `POST /rewrites/rewrite` - Rewrite entry (no save)
- `POST /rewrites/rewrite-and-save` - Rewrite and save
- `GET /rewrites/recent` - Get recent entries

### Admin (Requires Admin Role)
- `GET /admin/clients` - List all clients (admin view)
- `POST /admin/clients` - Create new client
- `PUT /admin/clients/{id}` - Update client
- `DELETE /admin/clients/{id}` - Delete client
- `POST /admin/clients/{id}/upload-guidelines` - Upload guidelines PDF
- `POST /admin/clients/{id}/upload-accepted-examples` - Upload accepted examples PDF
- `POST /admin/clients/{id}/upload-denied-examples` - Upload denied examples PDF
- `GET /admin/audit-events` - View audit trail
- `POST /admin/users` - Create user
- `GET /admin/users` - List users
- `DELETE /admin/users/{id}` - Delete user

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | ⚠️ Change required | JWT secret key |
| `CORS_ORIGINS` | localhost URLs | Comma-separated allowed origins |
| `DATABASE_URL` | SQLite | Database connection string |
| `OLLAMA_URL` | http://localhost:11434/api/generate | Ollama API endpoint |
| `MODEL_NAME` | qwen2.5:7b | LLM model to use |
| `MAX_UPLOAD_SIZE` | 10485760 (10MB) | Maximum file upload size in bytes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | JWT token expiration |
| `MIN_PASSWORD_LENGTH` | 8 | Minimum password length |
| `DEBUG` | false | Enable debug mode |

## Monitoring & Logging

### Structured Logging

The application uses structured logging with support for both JSON (production) and colored console output (development).

**Log Levels:**
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application operation
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

**Automatic Logging:**
- All API requests and responses (with timing)
- Request IDs for tracing
- Error exceptions with stack traces
- User actions and authentication events

**Log Output:**
```bash
# Development (colored console output)
uvicorn main:app --reload --port 9001

# Production (JSON logs to file)
# Logs are written to app.log
```

**Example Log Entry (JSON):**
```json
{
  "timestamp": "2025-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "app.middleware",
  "message": "Request completed: GET /health",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_ms": 15.23
}
```

### Health Check Endpoints

Monitor application health and dependencies:

**Basic Health Check:**
```bash
curl http://localhost:9001/health
# Response: {"status": "ok", "timestamp": "...", "version": "1.0.0", "checks": {}}
```

**Detailed Health Check:**
```bash
curl http://localhost:9001/health/detailed
```

Response includes:
- Database connectivity status
- Ollama service status
- Response times for each service
- Overall health status

**Kubernetes-Style Probes:**
```bash
# Liveness probe - is the app running?
curl http://localhost:9001/health/live

# Readiness probe - can the app serve traffic?
curl http://localhost:9001/health/ready
```

**Health Status Values:**
- `healthy` - All systems operational
- `degraded` - Non-critical service down (e.g., Ollama)
- `unhealthy` - Critical service down (e.g., Database)

### Error Tracking

All errors are automatically tracked with:
- Standardized error responses
- Request ID for tracing
- Detailed error logging
- Validation error details

**Standard Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "timestamp": "2025-01-15T10:30:45Z",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "details": {
      "fields": [
        {"field": "password", "message": "Password too short", "type": "value_error"}
      ]
    }
  }
}
```

### Request Tracing

Every API request gets a unique `X-Request-ID` header that can be used to trace the request through logs:

```bash
# Response headers include:
X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Use this ID to search logs and track down issues.

## Testing

### Running Tests

The application includes a comprehensive unit test suite using pytest:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run tests with coverage
pytest --cov=app tests/
```

### Test Coverage

Tests cover:
- ✅ Password validation rules
- ✅ Password hashing and verification
- ✅ JWT token creation and decoding
- ✅ Client ID validation
- ✅ Text input sanitization
- ✅ Authentication flows

### Writing Tests

Tests are located in the `tests/` directory. Example:

```python
def test_password_validation():
    """Test that valid passwords pass validation."""
    validate_password("Admin123")  # Should not raise
```

## Database

### Development (SQLite)
```bash
DATABASE_URL="sqlite:///./time_rewrite.db"
```

### Production (PostgreSQL Recommended)
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/time_rewrite"
```

### Database Migrations (Alembic)

This project uses Alembic for database schema migrations.

#### Initialize Database (First Time)
```bash
# The database tables are created automatically on first run
# But for production, use migrations:
alembic upgrade head
```

#### Create a New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/
# Then apply it:
alembic upgrade head
```

#### Rollback Migration
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

#### View Migration History
```bash
alembic current  # Show current revision
alembic history  # Show all revisions
```

### Database Indexes

The following indexes are automatically created for performance:

**TimeEntry:**
- `client_id` - Fast lookup by client
- `created_at` - Efficient date-based queries

**AuditEvent:**
- `timestamp` - Quick date-range queries
- `username` - Fast user activity lookups
- `client_id` - Efficient client filtering

**Clients, Users:**
- Primary key indexes on `id` and `username`

### Pagination

All list endpoints support pagination to handle large datasets efficiently.

**Parameters:**
- `page` - Page number (1-indexed, default: 1)
- `page_size` - Items per page (1-100, default: 20)

**Response Structure:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false
}
```

**Example:**
```bash
# Get page 2 with 50 items
GET /admin/audit-events?page=2&page_size=50

# Get recent time entries (first page, 20 items)
GET /rewrites/recent?page=1&page_size=20
```

## Troubleshooting

### Issue: "CORS policy" errors
**Solution**: Add your frontend URL to `CORS_ORIGINS` in `.env`

### Issue: "Failed to extract text from PDF"
**Solutions**:
- Ensure PDF is not encrypted
- Check if PDF contains actual text (not scanned images)
- Verify file size is under the limit

### Issue: "Password validation failed"
**Solution**: Ensure password meets requirements (uppercase, lowercase, number, min length)

### Issue: Ollama connection errors
**Solutions**:
- Verify Ollama is running: `ollama list`
- Check `OLLAMA_URL` in `.env`
- Ensure the model is pulled: `ollama pull qwen2.5:7b`

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black .
```

### Type Checking
```bash
mypy app/
```

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
