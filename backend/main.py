"""M4 Backend Entrypoint."""

from fastapi import FastAPI
from backend.api.router import router

app = FastAPI(title="ORCA-LIVING M4 Integration API")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
