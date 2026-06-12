import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api import auth, datasets, query

# Auto-initialize database tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataPilot AI Production Engine Gateway",
    version="1.0.0",
    docs_url="/api/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Core Auth"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Data Ingestion"])
app.include_router(query.router, prefix="/api/query", tags=["Cognitive Analyst AI"])

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "DataPilot Execution Core"}
