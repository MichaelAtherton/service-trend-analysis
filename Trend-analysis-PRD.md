# Product Requirements Document (PRD)
## AI Trend Analyzer API Service

---

## 1. Overview

**Product Name:** AI Trend Analyzer API  
**Version:** 1.0  
**Purpose:** RESTful API backend to power the AI Trend Dashboard, providing multi-pass trend detection, constitution-based filtering, and research paper corpus management.

---

## 2. Architecture

```
┌─────────────────┐         HTTP/REST        ┌──────────────────┐
│  React Frontend │ ◄────────────────────► │  Python API      │
│  (dashboard.jsx)│                         │  (FastAPI)       │
└─────────────────┘                         └──────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │  In-Memory Store │
                                            │  (Papers, Config)│
                                            └──────────────────┘
```

---

## 3. Core Features

### 3.1 Multi-Pass Trend Detection Engine
Implement the 4-pass algorithm currently in JavaScript:

- **Pass A: Emergence Detection**
  - Input: Paper corpus, date ranges (0-30 days, 30-60 days)
  - Logic: Calculate acceleration ratio (recent/historical ≥ 3.0x)
  - Output: Emerging techniques with severity (CRITICAL/HIGH)

- **Pass B: Maturation Detection**
  - Input: 90-day paper corpus
  - Logic: Calculate 12-week variance (relative variance < 20%), detect production signals
  - Output: Maturing techniques with stability metrics

- **Pass C: Decline Detection**
  - Input: Recent (0-30 days) vs historical (30-90 days)
  - Logic: Decline threshold (<30% of historical volume)
  - Output: Declining techniques with decline percentage

- **Pass D: Gap Detection**
  - Input: Mature techniques (≥10 papers in 90 days)
  - Logic: Find technique pairs with zero combined papers
  - Output: Research gaps with opportunity indicators

### 3.2 Constitution-Based Filtering
- Accept strategic focus areas as input
- Apply severity boosting based on keyword matches:
  - Emerging: 2+ matches → HIGH to CRITICAL
  - Maturing: 1+ "production" match → HIGH to CRITICAL
  - Gaps: Strategic keyword + technique match → MEDIUM to HIGH

### 3.3 Paper Corpus Management
- Store research papers with metadata (title, date, techniques, citations)
- Support CRUD operations
- Initial seed data: 40 sample papers (as per current dashboard.jsx)

---

## 4. API Specifications

### 4.1 Endpoints

#### `GET /api/v1/trends`
**Purpose:** Get all detected trends with filtering options

**Query Parameters:**
- `severity` (optional): Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
- `type` (optional): Filter by trend type (EMERGING, MATURING, DECLINING, GAP)
- `constitution` (optional): JSON string of constitution config

**Response:**
```json
{
  "trends": [
    {
      "id": "string",
      "type": "EMERGING | MATURING | DECLINING | GAP",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "technique": "string",
      "techniqueA": "string (for gaps)",
      "techniqueB": "string (for gaps)",
      "metrics": {
        "acceleration": "number (for emerging)",
        "stability": "string (for maturing)",
        "decline": "string (for declining)",
        "recentCount": "number",
        "historicalCount": "number",
        "totalPapers": "number",
        "productionSignals": "number"
      },
      "papers": ["string"],
      "recommendation": "string"
    }
  ],
  "summary": {
    "total": "number",
    "bySeverity": {
      "CRITICAL": "number",
      "HIGH": "number",
      "MEDIUM": "number",
      "LOW": "number"
    },
    "byType": {
      "EMERGING": "number",
      "MATURING": "number",
      "DECLINING": "number",
      "GAP": "number"
    }
  },
  "analysisDate": "ISO8601 string"
}
```

#### `POST /api/v1/constitution`
**Purpose:** Update constitution and get recalculated trends

**Request Body:**
```json
{
  "strategic_focus": ["string"],
  "priorities": {
    "latency": "string",
    "stability": "string"
  }
}
```

**Response:** Same as `GET /api/v1/trends`

#### `GET /api/v1/papers`
**Purpose:** Get all papers in corpus

**Query Parameters:**
- `technique` (optional): Filter by technique
- `startDate` (optional): Filter by date range start
- `endDate` (optional): Filter by date range end

**Response:**
```json
{
  "papers": [
    {
      "id": "string",
      "title": "string",
      "date": "ISO8601 string",
      "techniques": ["string"],
      "citations": "number"
    }
  ],
  "count": "number"
}
```

#### `POST /api/v1/papers`
**Purpose:** Add new paper to corpus

**Request Body:**
```json
{
  "title": "string",
  "date": "ISO8601 string",
  "techniques": ["string"],
  "citations": "number"
}
```

#### `GET /api/v1/health`
**Purpose:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "corpusSize": "number"
}
```

---

## 5. Technical Requirements

### 5.1 Technology Stack
- **Framework:** FastAPI (modern, async, auto-docs with OpenAPI)
- **Validation:** Pydantic models
- **CORS:** Enabled for local React dev server (port 3000)
- **Server:** Uvicorn (ASGI server)

### 5.2 Dependencies (for `pyproject.toml`)
```toml
dependencies = [
  "fastapi>=0.104.0",
  "uvicorn[standard]>=0.24.0",
  "pydantic>=2.5.0",
  "python-dateutil>=2.8.0"
]
```

### 5.3 Performance Requirements
- Response time: <100ms for trend detection (matches constitution priority)
- Support for corpus size: Up to 10,000 papers (future-proof)
- Concurrent requests: Handle 10+ simultaneous clients

### 5.4 Data Storage
- **Phase 1 (MVP):** In-memory storage (Python dict/list)
- **Phase 2 (Future):** PostgreSQL/MongoDB for persistence

---

## 6. Non-Functional Requirements

### 6.1 Documentation
- Auto-generated OpenAPI/Swagger docs at `/docs`
- ReDoc documentation at `/redoc`

### 6.2 Error Handling
- Return proper HTTP status codes (200, 400, 404, 500)
- Structured error responses:
```json
{
  "error": "string",
  "detail": "string",
  "code": "ERROR_CODE"
}
```

### 6.3 Logging
- Log all API requests with timestamps
- Log trend detection calculations for debugging
- Error stack traces for 500 errors

### 6.4 Testing
- Unit tests for each detection pass
- Integration tests for API endpoints
- Test coverage: >80%

---

## 7. Migration from Frontend

### Current State (dashboard.jsx)
- All logic client-side (532 lines)
- 40 hardcoded papers
- Constitution state managed in React

### Target State (API + Frontend)
- **Backend:** Python API with detection logic
- **Frontend:** React UI calls API, displays results
- **Benefits:**
  - Separation of concerns
  - Easier to test backend logic
  - Can swap frontend without changing backend
  - Backend can serve multiple clients (web, mobile, CLI)

---

## 8. Development Phases

### Phase 1: Core API (MVP)
- ✅ Implement 4-pass detection algorithm in Python
- ✅ Create FastAPI endpoints (GET /trends, GET /papers, GET /health)
- ✅ Seed 40 sample papers
- ✅ CORS configuration

### Phase 2: Constitution Support
- ✅ POST /constitution endpoint
- ✅ Dynamic severity boosting
- ✅ Constitution validation

### Phase 3: Paper Management
- ✅ POST /papers endpoint
- ✅ Paper validation (date format, techniques)

### Phase 4: Integration
- ✅ Update dashboard.jsx to call API
- ✅ Remove client-side detection logic
- ✅ Environment configuration (API_URL)

### Phase 5: Production Ready
- ⏳ Database persistence
- ⏳ Authentication/API keys
- ⏳ Rate limiting
- ⏳ Caching layer

---

## 9. Success Criteria

- ✅ API returns same results as current client-side logic
- ✅ Response time <100ms for trend detection
- ✅ Frontend fully functional using API
- ✅ 100% feature parity with current dashboard.jsx
- ✅ OpenAPI documentation complete

---

## 10. Out of Scope (v1.0)

- ❌ User authentication
- ❌ Database persistence
- ❌ Real-time updates (WebSocket)
- ❌ Paper scraping from ArXiv
- ❌ ML-based trend prediction
- ❌ Multi-tenancy

---

## 11. API Example Usage

```bash
# Get all trends
curl http://localhost:8000/api/v1/trends

# Filter by severity
curl http://localhost:8000/api/v1/trends?severity=CRITICAL

# Update constitution and get trends
curl -X POST http://localhost:8000/api/v1/constitution \
  -H "Content-Type: application/json" \
  -d '{"strategic_focus": ["real-time AI systems", "cost reduction"]}'

# Get papers
curl http://localhost:8000/api/v1/papers?technique=RAG
```

---

**Ready to proceed with implementation?**

