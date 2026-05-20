import os

from fastapi import FastAPI

from .routers import tasks
from .schemas import HealthResponse

app = FastAPI(title="Tasks API")

app.include_router(tasks.router)


@app.get("/health", response_model=HealthResponse)
def health() -> dict:
	env = os.getenv("APP_ENV", "local")
	return {"status": "ok", "env": env}
