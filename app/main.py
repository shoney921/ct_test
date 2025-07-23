from fastapi import FastAPI
from app.api import mocks

app = FastAPI()

app.include_router(mocks.router)