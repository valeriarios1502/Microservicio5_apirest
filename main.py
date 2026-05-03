from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import awswrangler as wr
import boto3
import os
import logging

from routers import peliculas, usuarios, foros

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = os.getenv("ATHENA_DATABASE", "glue_datalake")
S3_OUTPUT = os.getenv("ATHENA_S3_OUTPUT", "s3://cinetrack-results/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API Analytics Datalake...")
    boto3.setup_default_session(region_name=AWS_REGION)
    yield
    logger.info("🛑 Cerrando API...")

app = FastAPI(
    title="Analytics API - Datalake Películas",
    description="API REST para consultas analíticas sobre el datalake de películas, usuarios y foros.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(peliculas.router, prefix="/api/peliculas", tags=["Películas"])
app.include_router(usuarios.router,  prefix="/api/usuarios",  tags=["Usuarios"])
app.include_router(foros.router,     prefix="/api/foros",     tags=["Foros"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "mensaje": "Analytics API del Datalake funcionando",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}