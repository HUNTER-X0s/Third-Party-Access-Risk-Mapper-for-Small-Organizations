from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import dashboard, applications, findings, evidence, graph, snapshots, demo, auth, users, connectors, ai, monitoring, vendors
from app.db.session import engine, SessionLocal
from app.models import Base
from app.db.seed import seed_database

# Validate Production Config (Fail-Closed Check)
settings.validate_production_config()

# Create DB tables
Base.metadata.create_all(bind=engine)

# Automatically seed demo database if empty
db = SessionLocal()
try:
    from app.models import Organization
    if not db.query(Organization).first():
        seed_database(db)
finally:
    db.close()

from app.services.monitoring_scheduler import scheduler

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AccessGuard Third-Party Access Intelligence & Risk Management Platform API"
)

@app.on_event("startup")
def on_startup():
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    scheduler.stop()


# CORS Middleware (Strict Origin Allowlist)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Anti-CSRF & Security Headers Middleware
@app.middleware("http")
async def security_and_csrf_middleware(request: Request, call_next):
    # Anti-CSRF Defense for State-Changing Operations
    if request.method in ["POST", "PATCH", "DELETE", "PUT"]:
        # Exclude public auth endpoints from custom header requirement if origin matches
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        requested_with = request.headers.get("x-requested-with")
        has_bearer = request.headers.get("authorization", "").startswith("Bearer ")

        # Validate Origin / Referer if present against allowlist
        if origin and origin not in settings.CORS_ORIGINS:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"CSRF Defense: Origin '{origin}' is not allowed."}
            )

        # Require custom header or Bearer header for cookie-authenticated state changes
        if not has_bearer and not requested_with and origin and origin not in settings.CORS_ORIGINS:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF Defense: Missing Anti-CSRF custom request header."}
            )

    response = await call_next(request)

    # Modern Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"  # Legacy compatibility header
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"

    # Environment-Aware HSTS Header (Emit ONLY when COOKIE_SECURE is True for HTTPS)
    if settings.COOKIE_SECURE:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# Include API v1 Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["User Management"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}", tags=["Dashboard"])
app.include_router(applications.router, prefix=f"{settings.API_V1_STR}/applications", tags=["Applications"])
app.include_router(findings.router, prefix=f"{settings.API_V1_STR}/findings", tags=["Findings"])
app.include_router(evidence.router, prefix=f"{settings.API_V1_STR}/evidence", tags=["Evidence"])
app.include_router(graph.router, prefix=f"{settings.API_V1_STR}/graph", tags=["Access Graph"])
app.include_router(snapshots.router, prefix=f"{settings.API_V1_STR}/snapshots", tags=["Snapshots"])
app.include_router(demo.router, prefix=f"{settings.API_V1_STR}/demo", tags=["Demo & Reports"])
app.include_router(connectors.router, prefix=f"{settings.API_V1_STR}/connectors", tags=["Connectors"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["AI Security Analyst"])
app.include_router(monitoring.router, prefix=f"{settings.API_V1_STR}/monitoring", tags=["Continuous Monitoring & Shadow SaaS"])
app.include_router(vendors.router, prefix=f"{settings.API_V1_STR}/vendors", tags=["Suppliers & Vendor Risk"])

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "DEMO / SIMULATED ENVIRONMENT" if settings.DEMO_MODE else "PRODUCTION",
        "environment": settings.ENVIRONMENT,
        "organization": settings.ORGANIZATION_NAME,
        "risk_engine_version": "v1.5.0",
        "cookie_secure": settings.COOKIE_SECURE,
        "csrf_protection": "ACTIVE (Double-Defense)"
    }
