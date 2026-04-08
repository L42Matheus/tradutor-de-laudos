"""
Serviço de geocodificação para obter coordenadas de municípios.
Usa API do IBGE como fonte primária e Nominatim como fallback.
"""
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import httpx


_geo_cache: Dict[str, Dict[str, Any]] = {}
_cache_expiry: Dict[str, datetime] = {}
_CACHE_TTL = timedelta(hours=24)

_municipios_ibge: Optional[List[Dict[str, Any]]] = None
_municipios_por_estado_cache: Dict[str, List[Dict[str, str]]] = {}


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    """Obtém valor do cache se não expirado."""
    if key in _geo_cache and key in _cache_expiry:
        if datetime.now() < _cache_expiry[key]:
            return _geo_cache[key]
        else:
            del _geo_cache[key]
            del _cache_expiry[key]
    return None


def _cache_set(key: str, value: Dict[str, Any]) -> None:
    """Armazena valor no cache com TTL."""
    _geo_cache[key] = value
    _cache_expiry[key] = datetime.now() + _CACHE_TTL


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e caracteres especiais."""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', texto.lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


async def _carregar_municipios_ibge() -> List[Dict[str, Any]]:
    """Carrega lista completa de municípios do IBGE (cacheado)."""
    global _municipios_ibge

    if _municipios_ibge is not None:
        return _municipios_ibge

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
            )
            response.raise_for_status()
            _municipios_ibge = response.json()
            return _municipios_ibge
    except Exception:
        return []


def _extrair_municipio_de_clinica(nome_clinica: str) -> Optional[str]:
    """
    Tenta extrair nome do município do nome da clínica.
    Ex: "Hospital Regional de Campina Grande" -> "Campina Grande"
    """
    nome_lower = nome_clinica.lower()

    padroes = [
        r'(?:hospital|clinica|laboratorio|centro)\s+(?:regional|municipal|estadual)?\s*(?:de|do|da)?\s*(.+)',
        r'(.+?)\s*[-–]\s*(?:pb|sp|rj|mg|ba|pe|ce|rs|pr|sc|go|df|ma|pa|am|mt|ms|rn|al|se|pi|to|ro|ac|ap|rr|es)',
        r'(?:em|de|do|da)\s+(.+?)(?:\s*[-–]|$)',
    ]

    for padrao in padroes:
        match = re.search(padrao, nome_lower, re.IGNORECASE)
        if match:
            municipio = match.group(1).strip()
            municipio = re.sub(r'\s+', ' ', municipio)
            if len(municipio) >= 3:
                return municipio.title()

    return None


async def _buscar_municipio_ibge(nome_municipio: str) -> Optional[Dict[str, Any]]:
    """
    Busca município na API do IBGE por nome.
    Retorna dados do município incluindo coordenadas do centroide.
    """
    municipios = await _carregar_municipios_ibge()

    if not municipios:
        return None

    nome_normalizado = _normalizar_texto(nome_municipio)

    for mun in municipios:
        nome_mun = _normalizar_texto(mun.get("nome", ""))
        if nome_mun == nome_normalizado:
            uf = mun.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {})
            return {
                "municipio": mun["nome"],
                "estado": uf.get("sigla", ""),
                "ibge_id": mun["id"]
            }

    for mun in municipios:
        nome_mun = _normalizar_texto(mun.get("nome", ""))
        if nome_normalizado in nome_mun or nome_mun in nome_normalizado:
            uf = mun.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {})
            return {
                "municipio": mun["nome"],
                "estado": uf.get("sigla", ""),
                "ibge_id": mun["id"]
            }

    return None


def _extrair_geojson_coordinates(payload: Any) -> List[List[float]]:
    """
    Extrai coordenadas de respostas GeoJSON do IBGE.
    A API pode retornar FeatureCollection, Feature ou geometria direta.
    """
    if not isinstance(payload, dict):
        return []

    if "coordinates" in payload:
        return _flatten_coords(payload["coordinates"])

    geometry = payload.get("geometry")
    if isinstance(geometry, dict) and "coordinates" in geometry:
        return _flatten_coords(geometry["coordinates"])

    features = payload.get("features")
    if isinstance(features, list) and features:
        first_feature = features[0]
        if isinstance(first_feature, dict):
            feature_geometry = first_feature.get("geometry")
            if isinstance(feature_geometry, dict) and "coordinates" in feature_geometry:
                return _flatten_coords(feature_geometry["coordinates"])

    return []


async def _obter_coordenadas_municipio(ibge_id: int) -> Optional[Dict[str, float]]:
    """
    Obtém coordenadas do centroide do município via API do IBGE.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{ibge_id}",
                params={"formato": "application/vnd.geo+json"}
            )
            response.raise_for_status()
            geojson = response.json()

            coords = _extrair_geojson_coordinates(geojson)
            if coords:
                if coords:
                    lats = [c[1] for c in coords]
                    lons = [c[0] for c in coords]
                    return {
                        "lat": sum(lats) / len(lats),
                        "lon": sum(lons) / len(lons)
                    }
    except Exception:
        pass

    return None


def _flatten_coords(coords):
    """Achata lista de coordenadas aninhadas."""
    result = []
    if isinstance(coords, list):
        if len(coords) == 2 and isinstance(coords[0], (int, float)):
            return [coords]
        for item in coords:
            result.extend(_flatten_coords(item))
    return result


async def _buscar_nominatim(query: str) -> Optional[Dict[str, Any]]:
    """
    Fallback: busca localização via Nominatim (OpenStreetMap).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "country": "Brazil",
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1
                },
                headers={"User-Agent": "TraduzSaude/1.0 (Mestrado PPGTI/IFPB)"}
            )
            response.raise_for_status()
            results = response.json()

            if results:
                result = results[0]
                address = result.get("address", {})

                municipio = (
                    address.get("city") or
                    address.get("town") or
                    address.get("municipality") or
                    address.get("county")
                )

                estado = address.get("state")
                estado_sigla = _estado_para_sigla(estado) if estado else None

                if municipio and estado_sigla:
                    return {
                        "municipio": municipio,
                        "estado": estado_sigla,
                        "lat": float(result["lat"]),
                        "lon": float(result["lon"])
                    }
    except Exception:
        pass

    return None


def _estado_para_sigla(estado: str) -> Optional[str]:
    """Converte nome de estado para sigla UF."""
    estados = {
        "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM",
        "bahia": "BA", "ceara": "CE", "distrito federal": "DF",
        "espirito santo": "ES", "goias": "GO", "maranhao": "MA",
        "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
        "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE",
        "piaui": "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN",
        "rio grande do sul": "RS", "rondonia": "RO", "roraima": "RR",
        "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO"
    }
    return estados.get(_normalizar_texto(estado))


async def geocodificar(nome_clinica: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Geocodifica uma clínica/hospital para obter município e coordenadas.

    Args:
        nome_clinica: Nome da clínica ou hospital extraído do laudo

    Returns:
        Dict com municipio, estado (2 chars), lat, lon ou None se não encontrado
    """
    if not nome_clinica:
        return None

    cache_key = _normalizar_texto(nome_clinica)
    cached = _cache_get(cache_key)
    if cached:
        return cached

    municipio_extraido = _extrair_municipio_de_clinica(nome_clinica)

    if municipio_extraido:
        resultado_ibge = await _buscar_municipio_ibge(municipio_extraido)
        if resultado_ibge:
            coords = await _obter_coordenadas_municipio(resultado_ibge["ibge_id"])
            if coords:
                resultado = {
                    "municipio": resultado_ibge["municipio"],
                    "estado": resultado_ibge["estado"],
                    "lat": coords["lat"],
                    "lon": coords["lon"]
                }
                _cache_set(cache_key, resultado)
                return resultado

    resultado_nominatim = await _buscar_nominatim(nome_clinica)
    if resultado_nominatim:
        _cache_set(cache_key, resultado_nominatim)
        return resultado_nominatim

    if municipio_extraido:
        resultado_nominatim = await _buscar_nominatim(f"{municipio_extraido}, Brasil")
        if resultado_nominatim:
            _cache_set(cache_key, resultado_nominatim)
            return resultado_nominatim

    return None


async def geocodificar_municipio(
    municipio: str,
    estado: str,
    municipio_ibge_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Geocodifica diretamente pelo nome do município e estado.
    Usado quando o usuário confirma manualmente a localização.

    Args:
        municipio: Nome do município
        estado: Sigla do estado (2 chars)

    Returns:
        Dict com municipio, estado, lat, lon ou None
    """
    cache_key = f"{_normalizar_texto(municipio)}_{estado.lower()}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if municipio_ibge_id:
        try:
            coords = await _obter_coordenadas_municipio(int(municipio_ibge_id))
            if coords:
                resultado = {
                    "municipio": municipio,
                    "estado": estado.upper(),
                    "lat": coords["lat"],
                    "lon": coords["lon"]
                }
                _cache_set(cache_key, resultado)
                return resultado
        except ValueError:
            pass

    resultado_ibge = await _buscar_municipio_ibge(municipio)
    if resultado_ibge and resultado_ibge["estado"].upper() == estado.upper():
        coords = await _obter_coordenadas_municipio(resultado_ibge["ibge_id"])
        if coords:
            resultado = {
                "municipio": resultado_ibge["municipio"],
                "estado": resultado_ibge["estado"],
                "lat": coords["lat"],
                "lon": coords["lon"]
            }
            _cache_set(cache_key, resultado)
            return resultado

    resultado_nominatim = await _buscar_nominatim(f"{municipio}, {estado}, Brasil")
    if resultado_nominatim:
        _cache_set(cache_key, resultado_nominatim)
        return resultado_nominatim

    return None


async def listar_municipios_por_estado(estado: str) -> List[Dict[str, str]]:
    """
    Lista todos os municípios de um estado.
    Usado para popular dropdown de seleção manual.

    Args:
        estado: Sigla do estado (2 chars)

    Returns:
        Lista de dicts com id e nome dos municípios
    """
    estado = estado.upper()

    if estado in _municipios_por_estado_cache:
        return _municipios_por_estado_cache[estado]

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado}/municipios"
            )
            response.raise_for_status()
            municipios = response.json()

        resultado = [
            {
                "id": str(mun["id"]),
                "nome": mun["nome"],
            }
            for mun in municipios
            if mun.get("id") and mun.get("nome")
        ]
        resultado.sort(key=lambda x: x["nome"])
        _municipios_por_estado_cache[estado] = resultado
        return resultado
    except Exception:
        return []
