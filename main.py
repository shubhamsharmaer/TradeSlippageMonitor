from fastapi import FastAPI
from Config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def get_health():
    return {
        "message": "Welcome to the Leakage Detector API",
    }, 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
