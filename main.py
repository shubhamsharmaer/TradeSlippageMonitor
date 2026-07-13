from fastapi import FastAPI
from config import settings
from routes import mismatch, get_bt_algo, get_lt_algo, get_clients, get_brokers
from fastapi.middleware.cors import CORSMiddleware

# from scout_apm.api import Config
# from scout_apm.async_.starlette import ScoutMiddleware
from contextlib import asynccontextmanager
from mcp_server import mcp

mcp_app = mcp.http_app(path="/")   # ASGI app for streamable-HTTP transport


# Config.set(
#     key="nS5gkS1eyPEPVMsyedNl",
#     name="Leakage Backend",
#     monitor=True,
# )

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        yield

app = FastAPI(title="LiveToBacktestSlippage", lifespan=lifespan)

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
app.mount("/mcp", mcp_app)

@app.get("/health")
async def get_health():
    return {
        "message": "Welcome to the Leakage Detector API",
    }, 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)
