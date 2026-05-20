from fastapi import FastAPI

from .routers import tasks

app = FastAPI(title="Tasks API")

app.include_router(tasks.router)
