from fastapi import FastAPI
from config import settings
from routes import mismatch, get_bt_algo, get_lt_algo, get_clients, get_brokers
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="LiveToBacktestSlippage")

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

@app.get("/health")
async def get_health():
    return {
        "message": "Welcome to the Leakage Detector API",
    }, 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
