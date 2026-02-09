"""
FastAPI entry point - Traduz Saúde API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.routes import translate, validate, usage, support

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print("👋 Encerrando aplicação")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para tradução de documentos médicos em linguagem acessível",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(translate.router, prefix="/api/v1/translate", tags=["Tradução"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["Validação"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["Uso"])
app.include_router(support.router, prefix="/api/v1/support", tags=["Apoio"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.get("/", tags=["Root"])
async def root():
    """Rota raiz com informações da API"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
