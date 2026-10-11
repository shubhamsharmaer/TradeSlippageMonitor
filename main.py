from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from config import settings
from routes import mismatch, get_bt_algo, get_lt_algo, get_clients, get_brokers, trade_dates
from fastapi.middleware.cors import CORSMiddleware

# from scout_apm.api import Config
# from scout_apm.async_.starlette import ScoutMiddleware
from contextlib import asynccontextmanager
from mcp_server import mcp

mcp_app = mcp.http_app(path="/")   # ASGI app for streamable-HTTP transport
BASE_DIR = Path(__file__).resolve().parent


# Config.set(
#     key="nS5gkS1eyPEPVMsyedNl",
#     name="Leakage Backend",
#     monitor=True,
# )

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        yield

app = FastAPI(title="Slippage Monitor", lifespan=lifespan)

# app.add_middleware(ScoutMiddleware)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mismatch.router)
app.include_router(get_bt_algo.router)
app.include_router(get_lt_algo.router)
app.include_router(get_clients.router)
app.include_router(get_brokers.router)
app.include_router(trade_dates.router)
app.mount("/mcp", mcp_app)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "templates" / "demo.html")


@app.get("/health")
async def get_health():
    return {
        "message": "Welcome to the Leakage Detector API",
        "mode": settings.app_mode,
        "demo_mode": settings.is_demo_mode,
    }, 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)
