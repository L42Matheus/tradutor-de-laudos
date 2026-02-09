"""
Configuração dos testes - fixtures compartilhadas
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import asyncio

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para toda a sessão de testes"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Cliente de teste síncrono"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Cliente de teste assíncrono"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_medical_text():
    """Texto de exemplo de laudo médico"""
    return """
    HEMOGRAMA COMPLETO

    Hemácias: 4.5 milhões/mm³ (VR: 4.0-5.5)
    Hemoglobina: 14.0 g/dL (VR: 12.0-16.0)
    Hematócrito: 42% (VR: 36-46%)
    Leucócitos: 7.500/mm³ (VR: 4.000-11.000)
    Plaquetas: 250.000/mm³ (VR: 150.000-400.000)
    """


@pytest.fixture
def sample_non_medical_text():
    """Texto de exemplo não médico"""
    return """
    CONTA DE LUZ

    Consumo: 150 kWh
    Valor: R$ 120,00
    Vencimento: 15/03/2024
    """
