"""
Rotas para consulta de localização (municípios e estados).
Usado para popular dropdowns de confirmação manual de localização.
"""
from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.geocodificacao_service import listar_municipios_por_estado


router = APIRouter()


ESTADOS_BRASIL = [
    {"sigla": "AC", "nome": "Acre"},
    {"sigla": "AL", "nome": "Alagoas"},
    {"sigla": "AP", "nome": "Amapá"},
    {"sigla": "AM", "nome": "Amazonas"},
    {"sigla": "BA", "nome": "Bahia"},
    {"sigla": "CE", "nome": "Ceará"},
    {"sigla": "DF", "nome": "Distrito Federal"},
    {"sigla": "ES", "nome": "Espírito Santo"},
    {"sigla": "GO", "nome": "Goiás"},
    {"sigla": "MA", "nome": "Maranhão"},
    {"sigla": "MT", "nome": "Mato Grosso"},
    {"sigla": "MS", "nome": "Mato Grosso do Sul"},
    {"sigla": "MG", "nome": "Minas Gerais"},
    {"sigla": "PA", "nome": "Pará"},
    {"sigla": "PB", "nome": "Paraíba"},
    {"sigla": "PR", "nome": "Paraná"},
    {"sigla": "PE", "nome": "Pernambuco"},
    {"sigla": "PI", "nome": "Piauí"},
    {"sigla": "RJ", "nome": "Rio de Janeiro"},
    {"sigla": "RN", "nome": "Rio Grande do Norte"},
    {"sigla": "RS", "nome": "Rio Grande do Sul"},
    {"sigla": "RO", "nome": "Rondônia"},
    {"sigla": "RR", "nome": "Roraima"},
    {"sigla": "SC", "nome": "Santa Catarina"},
    {"sigla": "SP", "nome": "São Paulo"},
    {"sigla": "SE", "nome": "Sergipe"},
    {"sigla": "TO", "nome": "Tocantins"},
]


class Estado(BaseModel):
    sigla: str
    nome: str


class Municipio(BaseModel):
    id: str
    nome: str


class EstadosResponse(BaseModel):
    success: bool
    data: List[Estado]


class MunicipiosResponse(BaseModel):
    success: bool
    data: List[Municipio]
    estado: str


@router.get("/estados", response_model=EstadosResponse)
async def listar_estados() -> EstadosResponse:
    """
    Lista todos os estados brasileiros.
    """
    return EstadosResponse(
        success=True,
        data=[Estado(**e) for e in ESTADOS_BRASIL]
    )


@router.get("/municipios", response_model=MunicipiosResponse)
async def listar_municipios(
    estado: str = Query(..., min_length=2, max_length=2, description="Sigla do estado (UF)")
) -> MunicipiosResponse:
    """
    Lista todos os municípios de um estado.

    - **estado**: Sigla do estado (ex: PB, SP, RJ)
    """
    estado = estado.upper()

    if estado not in [e["sigla"] for e in ESTADOS_BRASIL]:
        return MunicipiosResponse(
            success=False,
            data=[],
            estado=estado
        )

    municipios = await listar_municipios_por_estado(estado)

    return MunicipiosResponse(
        success=True,
        data=[Municipio(**m) for m in municipios],
        estado=estado
    )
