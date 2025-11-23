from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.database import Base, engine
from src.routers import devices

app = FastAPI(
    title="ESP Edge Backend",
    version="0.1.0",
    description="Backend for ESP to RPi sensor ingestion",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(devices.router, prefix="/api", tags=["devices"])


# --- Startup / Shutdown ---
@app.on_event("startup")
async def on_startup():
    # Auto-create tables (dev-only). For production: use Alembic.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
