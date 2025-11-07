# Service Management Guide

## 🚀 Services Running

Both services are now operational:

```bash
✅ Embedding Server:    http://localhost:8765
✅ Extraction Service:  http://localhost:8000
```

## 📋 Service Details

### Embedding Server (Port 8765)
- **Purpose**: FastAPI wrapper exposing BERTrend's sentence-transformers model via REST API
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **GPU**: Using Apple Silicon MPS acceleration
- **PID File**: `embedding-server.pid`
- **Log File**: `embedding-server.log`

### Extraction Service (Port 8000)
- **Purpose**: AI Technique Extraction Service - orchestrates the full pipeline
- **API Prefix**: `/api/v1`
- **PID File**: `extraction-service.pid`
- **Log File**: `extraction-service.log`

## 🔍 Monitoring Services

### Check Service Status
```bash
# Check if services are running
lsof -i :8765  # Embedding server
lsof -i :8000  # Extraction service

# View logs in real-time
tail -f embedding-server.log
tail -f extraction-service.log
```

### Health Checks
```bash
# Embedding server health
curl http://localhost:8765/health

# Extraction service health
curl http://localhost:8000/api/v1/health

# Test embedding endpoint
curl -X POST http://localhost:8765/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["transformer neural network", "bert language model"]}'
```

## 🛑 Stopping Services

### Stop Individual Service
```bash
# Stop embedding server
kill $(cat embedding-server.pid)
rm embedding-server.pid

# Stop extraction service
kill $(cat extraction-service.pid)
rm extraction-service.pid
```

### Stop All Services
```bash
# Stop both services
kill $(cat embedding-server.pid) $(cat extraction-service.pid)
rm embedding-server.pid extraction-service.pid
```

## 🔄 Restarting Services

### Restart Embedding Server
```bash
# Stop
kill $(cat embedding-server.pid) 2>/dev/null
rm embedding-server.pid 2>/dev/null

# Start
cd services/embedding-server && \
  ../../.venv/bin/python3 start_server.py > ../../embedding-server.log 2>&1 &
echo $! > ../../embedding-server.pid
cd ../..

# Verify
sleep 3 && curl http://localhost:8765/health
```

### Restart Extraction Service
```bash
# Stop
kill $(cat extraction-service.pid) 2>/dev/null
rm extraction-service.pid 2>/dev/null

# Start
cd services/technique-extraction && \
  OPENAI_API_KEY="your-openai-api-key-here" \
  EMBEDDING_SERVER_URL="http://localhost:8765" \
  EMBEDDING_CLIENT_ID="extraction-service" \
  EMBEDDING_CLIENT_SECRET="dev-secret" \
  ALLOWED_API_KEYS="test-key-1,test-key-2" \
  PORT=8000 \
  LOG_LEVEL=INFO \
  ../../.venv/bin/python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 > ../../extraction-service.log 2>&1 &
echo $! > ../../extraction-service.pid
cd ../..

# Verify
sleep 2 && curl http://localhost:8000/api/v1/health
```

## 🧪 Running Tests

### Prerequisites
1. **Both services must be running**
2. **Environment variables set** (already configured in `.env.test`)
3. **Test fixtures in place** (8 labeled papers in `tests/fixtures/`)

### Run Full Test Suite
```bash
cd services/technique-extraction

# Run all tests
../../.venv/bin/python3 -m pytest tests/ -v

# Run specific test category
../../.venv/bin/python3 -m pytest tests/test_pipeline.py -v
../../.venv/bin/python3 -m pytest tests/test_error_handling.py -v
../../.venv/bin/python3 -m pytest tests/test_monitoring.py -v
../../.venv/bin/python3 -m pytest tests/test_taxonomy.py -v

# Generate HTML report
../../.venv/bin/python3 -m pytest tests/ --html=test-reports/report.html
```

### Expected Test Duration
- **Full suite**: ~4 minutes (8 papers × 30s/paper + overhead)
- **Single test**: ~30 seconds per paper
- **API cost**: ~$0.001 per full run (OpenAI GPT-4o-mini for LLM validation)

## 📊 API Endpoints

### Embedding Server (`:8765`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/embed` | POST | Generate embeddings |
| `/docs` | GET | Interactive API docs (Swagger UI) |

### Extraction Service (`:8000`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/extract/techniques` | POST | Extract techniques from papers |
| `/docs` | GET | Interactive API docs (Swagger UI) |

## 📝 Troubleshooting

### Embedding Server Won't Start
```bash
# Check if port is already in use
lsof -i :8765

# Check logs for errors
tail -50 embedding-server.log

# Common issues:
# - Missing dependencies: pip install fastapi uvicorn sentence-transformers
# - Model download failed: Check internet connection
# - GPU/MPS issues: Service will fall back to CPU
```

### Extraction Service Won't Start
```bash
# Check if port is already in use
lsof -i :8000

# Check logs for errors
tail -50 extraction-service.log

# Common issues:
# - Missing environment variables: Check .env or export manually
# - Embedding server not running: Start embedding server first
# - Invalid OpenAI API key: Verify OPENAI_API_KEY
```

### Tests Failing
```bash
# Verify both services are running
curl http://localhost:8765/health
curl http://localhost:8000/api/v1/health

# Check .env.test configuration
cat services/technique-extraction/.env.test

# Run tests with verbose output
../../.venv/bin/python3 -m pytest tests/ -v -s --log-cli-level=DEBUG
```

## 🎯 Next Steps

1. **Run tests**: Validate the MVP implementation
   ```bash
   cd services/technique-extraction
   ../../.venv/bin/python3 -m pytest tests/test_pipeline.py -v
   ```

2. **Review test results**: Check for any failing tests and review confidence scores

3. **Iterate on implementation**: Fix any issues identified by tests

4. **Phase 7 (Optional)**: CI/CD integration, GitHub Actions, deployment scripts

## 📚 Documentation

- **API Docs**: http://localhost:8765/docs (Embedding Server)
- **API Docs**: http://localhost:8000/docs (Extraction Service)
- **Specs**: `specs/001-technique-extraction/spec.md`
- **Plan**: `specs/001-technique-extraction/plan.md`
- **Tasks**: `specs/001-technique-extraction/tasks.md`
- **Test Guide**: `services/technique-extraction/tests/README.md`

