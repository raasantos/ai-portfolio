from fastapi import FastAPI
from router import router

app = FastAPI(title="Job Extractor")
app.include_router(router)