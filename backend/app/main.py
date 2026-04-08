"""
FastAPI entry point - Traduz Saude API.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, epidemio, history, localizacao, revisao, support, translate, usage, validate
from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicacao."""
    print(f"Iniciando {settings.app_name} v{settings.app_version}")
    init_db()
    print("Banco de dados inicializado")
    yield
    print("Encerrando aplicacao")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para traducao de documentos medicos em linguagem acessivel",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(history.router, prefix="/api/v1/history", tags=["Historico"])
app.include_router(translate.router, prefix="/api/v1/translate", tags=["Traducao"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["Validacao"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["Uso"])
app.include_router(support.router, prefix="/api/v1/support", tags=["Apoio"])
app.include_router(epidemio.router, prefix="/api/v1/epidemio", tags=["Epidemiologia"])
app.include_router(localizacao.router, prefix="/api/v1/localizacao", tags=["Localizacao"])
app.include_router(revisao.router, prefix="/api/v1/revisao", tags=["Revisao"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
