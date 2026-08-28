# 03 — Technology Evaluation
# AccessGuard: Technology Stack Analysis & Recommendations

**Document Type:** Technology Evaluation — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  

---

## Evaluation Criteria

Each technology is evaluated against:

1. **Speed** — How quickly can a team become productive?
2. **Reliability** — Is this a mature, trusted choice?
3. **Developer Productivity** — Does it remove boilerplate and accelerate delivery?
4. **Security** — Does it have known security concerns? Does it help or hinder security?
5. **Maintainability** — Can this be maintained over time by a small team?
6. **Hackathon Suitability** — Is this realistic to implement in a compressed timeline?
7. **Production Evolution** — Could this evolve into a production system without major rewrites?

---

## 1. Frontend Framework

### Evaluated Options

| Option | Notes |
|---|---|
| **React + TypeScript** | Industry standard; vast ecosystem; component reuse; strong type safety |
| Vue.js + TypeScript | Good alternative but smaller ecosystem for security tooling |
| Angular | Opinionated; good for enterprise; complex for a small team in a hackathon |
| SvelteKit | Modern, fast, but smaller ecosystem; less familiar tooling |
| Next.js | Full-stack; adds complexity if API is already FastAPI |

### Decision: **React 18 + TypeScript**

**Justification:**
- TypeScript prevents a significant class of runtime bugs, especially important when handling complex security data structures
- React's component model aligns perfectly with AccessGuard's modular views (Dashboard, Applications, Risk Map)
- The ecosystem provides exactly the libraries we need (React Flow, Recharts, shadcn/ui)
- Team productivity is highest with the most widely-known framework
- Production-ready; the same stack used by security tools like Panther, Lacework, and Wiz

**Security note:** TypeScript's strict type system reduces injection surface compared to plain JavaScript by catching type coercion errors that could be exploited.

---

## 2. UI Styling

### Evaluated Options

| Option | Notes |
|---|---|
| **Tailwind CSS** | Utility-first; rapid iteration; no CSS naming battles |
| Vanilla CSS | Maximum control but very slow for complex UIs |
| CSS Modules | Good isolation but still slow for rapid development |
| Styled Components | CSS-in-JS; runtime cost; less hackathon-friendly |
| shadcn/ui + Tailwind | Component library on top of Tailwind; pre-built accessible components |

### Decision: **Tailwind CSS + shadcn/ui**

**Justification:**
- shadcn/ui provides production-quality, accessible components (Data Tables, Dialogs, Badges, Cards) that match AccessGuard's needs exactly
- Tailwind enables rapid design iteration without writing CSS files
- Together they can produce a genuinely premium security dashboard aesthetic
- shadcn/ui components are highly accessible (WCAG AA) out of the box
- Radix UI primitives underneath shadcn/ui are well-tested

---

## 3. Graph Visualization

### Evaluated Options

| Option | Notes |
|---|---|
| **React Flow** | Built for node-edge graphs; excellent for data flow and attack path visualization |
| D3.js | Very powerful but extremely high learning curve; not hackathon-appropriate |
| Cytoscape.js | Network graphs; good but heavier and less React-native |
| Sigma.js | High-performance but minimal React integration |
| ECharts | Good general charts; not ideal for interactive node-edge graphs |

### Decision: **React Flow**

**Justification:**
- React Flow is purpose-built for exactly the type of interactive node-edge graph AccessGuard needs for data-flow visualization and attack-path display
- Has React-native API; integrates seamlessly with our React frontend
- Handles layouts, dragging, zooming, and custom node rendering out of the box
- Used in production by many security tools
- Much faster to implement than D3.js for this specific use case

---

## 4. Additional Charting

### Decision: **Recharts**

For non-graph visualizations (posture trend lines, risk histograms, heatmaps):
- Recharts provides React-native chart components
- Responsive, well-documented, and declarative
- Lightweight alternative to Chart.js which is not React-native

---

## 5. Backend Framework

### Evaluated Options

| Option | Notes |
|---|---|
| **FastAPI (Python)** | Modern async Python; auto-generated OpenAPI docs; Pydantic validation |
| Django REST Framework | Mature but heavy; Django ORM is opinionated |
| Flask + extensions | Lightweight but requires assembling many parts manually |
| Node.js + Express | JavaScript full-stack; less natural for security/data-science workloads |
| Node.js + NestJS | TypeScript, structured; good for large teams; less data-science-friendly |
| Go + Chi/Gin | Excellent performance; less rapid for hackathon; smaller ecosystem for ML |

### Decision: **FastAPI (Python 3.12+)**

**Justification:**
- FastAPI generates OpenAPI documentation automatically — essential for a hackathon demo
- Pydantic v2 provides rigorous input validation that directly supports our "all input is untrusted" security principle
- Python's data-science ecosystem (numpy, pandas if needed for analytics) is a natural fit for the risk engine
- Async support handles concurrent connector polling efficiently
- Type hints throughout reduce runtime errors
- FastAPI's dependency injection system makes authentication/authorization middleware clean and testable
- Uvicorn ASGI server is production-capable

**Security advantages:**
- Pydantic validation automatically rejects malformed input
- FastAPI's Depends() system makes it easy to inject auth checks on every endpoint
- OpenAPI schema makes API contract visible and testable

---

## 6. Database

### Evaluated Options

| Option | Notes |
|---|---|
| **PostgreSQL** | Production-grade; excellent JSON support; row-level security; full text search |
| SQLite | Zero-config; perfect for demo mode; single file |
| MySQL/MariaDB | Fine but fewer advanced features than PostgreSQL |
| MongoDB | Document store; not ideal for relational security data with complex joins |
| Supabase | PostgreSQL-as-a-service; adds external dependency |

### Decision: **PostgreSQL (primary) + SQLite (demo/test)**

**Justification:**
- PostgreSQL's Row-Level Security (RLS) provides an additional database-layer enforcement of tenant isolation — defense-in-depth
- JSONB columns can store variable permission structures from different providers
- Full-text search for application/vendor search functionality
- SQLite for local demo allows running without a PostgreSQL server — important for hackathon portability
- SQLAlchemy as ORM supports both PostgreSQL and SQLite with the same code (minimal connection string change)

**Multi-database strategy:**
```
Development/Demo: SQLite  →  DEMO_MODE=true
Production/Full:  PostgreSQL  →  DATABASE_URL=postgresql://...
```

---

## 7. ORM & Data Layer

### Decision: **SQLAlchemy 2.0 + Alembic**

**Justification:**
- SQLAlchemy 2.0 has a modern async interface compatible with FastAPI's async model
- Alembic provides database migration management — essential for evolving the schema over time
- Pydantic models separate from SQLAlchemy models (clean layering: DB → ORM → Schema → API)
- Alembic migrations allow schema to be tracked in version control

---

## 8. Authentication

### Evaluated Options

| Option | Notes |
|---|---|
| **JWT (HS256/RS256) + PKCE** | Standard; stateless; secure if implemented correctly |
| Session-based auth | Simple but not suitable for API-first architecture |
| Auth0 / Clerk | Third-party dependency; adds complexity; introduces external trust boundary |
| Keycloak | Full IAM; overkill for hackathon but credible for production |

### Decision: **JWT (RS256) + PKCE for OAuth flows**

**Justification:**
- RS256 (asymmetric signing) is more secure than HS256 as it doesn't require sharing the secret
- PKCE is required by RFC 9700 for all public clients — showing compliance with modern OAuth standards
- Stateless JWT is compatible with FastAPI's async model
- Implementation in python-jose / pyjwt is well-tested
- Tokens must be short-lived (15 minutes access, 7-day refresh) with refresh token rotation

**Access token storage:** HttpOnly cookies preferred over localStorage to prevent XSS token theft.

---

## 9. Background Jobs

### Evaluated Options

| Option | Notes |
|---|---|
| **Celery + Redis** | Production-grade; widely used; good for periodic connector polling |
| APScheduler | Simpler; in-process; good for hackathon |
| FastAPI BackgroundTasks | Built-in; suitable for simple fire-and-forget tasks |
| RQ (Redis Queue) | Simpler than Celery; Redis-backed |

### Decision: **APScheduler (hackathon) → Celery + Redis (production)**

**Justification:**
- APScheduler requires no additional infrastructure for the hackathon demo
- Clean interface to schedule connector refresh jobs
- Architecture must be designed so the job logic can be extracted to Celery workers later
- Celery + Redis documented as the production target in the architectural decision log

---

## 10. Caching

### Decision: **Application-level caching first; Redis if justified**

**Justification:**
- Risk scores cached in the database with a `last_calculated` timestamp
- Python lru_cache for frequently accessed static data (permission normalization tables)
- Redis only introduced if profiling shows it's necessary
- Avoid premature optimization — Redis adds operational complexity

---

## 11. AI Layer

### Evaluated Options

| Option | Notes |
|---|---|
| **Google Gemini 1.5 Pro / 2.0 Flash** | Multimodal; large context window; good for analysis |
| OpenAI GPT-4o | Strong; widely known; but OpenAI dependency |
| Anthropic Claude | Strong reasoning; good for analysis |
| Local Ollama model | No API dependency; but lower quality; slower |

### Decision: **Google Gemini 2.0 Flash (primary) with graceful degradation**

**Justification:**
- Google Gemini is well-suited to structured security analysis tasks
- Large context window can hold full permission inventories for analysis
- Gemini 2.0 Flash provides fast responses for chat-style AI analyst interactions
- System must function fully if AI is unavailable (graceful degradation required)
- AI prompts are server-constructed — never user-controlled raw prompts
- All AI output is clearly labeled as "AI Suggestion" in the UI

**Security controls on AI integration:**
- AI layer is isolated in a dedicated module
- Risk scores never passed TO the AI as something to validate — only passed for EXPLANATION
- AI output is sanitized before display (prevent prompt injection output from rendering as HTML)
- AI context injected from server-side sanitized data only

---

## 12. Report Generation

### Decision: **WeasyPrint (PDF) + JSON export**

**Justification:**
- WeasyPrint converts HTML/CSS to PDF — allows reusing frontend report templates
- JSON export allows integration with other tools
- No complex PDF library required; report templates maintain consistent styling
- Alternative: ReportLab (more programmatic, less designer-friendly)

---

## 13. API Documentation

### Decision: **FastAPI Auto-Generated OpenAPI 3.1 + ReDoc**

- FastAPI generates complete OpenAPI specification automatically
- ReDoc provides a clean, professional documentation UI
- OpenAPI spec can be used with API testing tools (Postman, HTTPie)
- Demonstrates API-first development discipline to judges

---

## 14. Testing

| Layer | Tool |
|---|---|
| Backend unit tests | pytest + pytest-asyncio |
| API integration tests | httpx (async test client for FastAPI) |
| Frontend unit tests | Vitest + React Testing Library |
| E2E tests (if time permits) | Playwright |
| Security tests | Custom pytest test suite for auth, tenant isolation, and input validation |

---

## 15. Containerization & Deployment

### Decision: **Docker + Docker Compose**

**Justification:**
- Docker Compose allows the entire stack to run locally with one command: `docker compose up`
- Critical for hackathon demo portability
- Compose file defines all services: frontend (nginx), backend (uvicorn), database (postgres)
- Production path: same containers deployed to any container-capable platform (GCP Cloud Run, AWS ECS, etc.)

---

## 16. Reverse Proxy

### Decision: **Nginx**

- Serves the compiled React frontend as static files
- Proxies `/api/` requests to the FastAPI backend
- Handles SSL termination in production
- Single nginx container in Docker Compose

---

## 17. Monitoring (Hackathon Scope)

### Decision: **Structured logging (JSON) to stdout**

- Python `structlog` for structured JSON logs
- Docker Compose collects stdout logs
- Production path: ship to Cloud Logging / ELK / Grafana Loki
- No metrics infrastructure in hackathon scope

---

## Recommended Technology Stack Summary

| Layer | Technology | Version |
|---|---|---|
| Frontend | React | 18.x |
| Language (FE) | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.x |
| UI Components | shadcn/ui + Radix UI | Latest |
| Graph Visualization | React Flow | 11.x |
| Charts | Recharts | 2.x |
| Backend | FastAPI | 0.115.x |
| Language (BE) | Python | 3.12+ |
| Input Validation | Pydantic v2 | 2.x |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | 1.x |
| Database (demo) | SQLite | 3.x |
| Database (prod) | PostgreSQL | 16.x |
| Auth | python-jose + JWT | Latest |
| Background Jobs | APScheduler (demo) | 3.x |
| AI | Google Gemini 2.0 Flash | API |
| PDF Generation | WeasyPrint | Latest |
| Testing (BE) | pytest + httpx | Latest |
| Testing (FE) | Vitest + RTL | Latest |
| Container | Docker + Compose | Latest |
| Web Server | Nginx | 1.25+ |
| Process Manager | Uvicorn | 0.30+ |

---

## Technologies Explicitly Rejected

| Technology | Reason for Rejection |
|---|---|
| Redux (for state) | Zustand is simpler and sufficient; Redux overkill for this scope |
| GraphQL | REST is sufficient; GraphQL adds complexity without benefit here |
| Kubernetes | Overkill for hackathon; use Docker Compose |
| Microservices | Modular monolith preferred (see DECISION-LOG) |
| Elasticsearch | Not justified at this data scale |
| Kafka | Not justified; APScheduler sufficient |
| Terraform | Infrastructure-as-Code documented as future capability |

---

*Technology evaluation version 1.0 — Decisions recorded in DECISION-LOG.md.*
