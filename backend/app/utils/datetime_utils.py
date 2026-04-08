"""
Helpers de data/hora padronizados para o fuso do Brasil.
"""
from datetime import datetime
from zoneinfo import ZoneInfo


BRAZIL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def brazil_now() -> datetime:
    """
    Retorna a hora atual no fuso de Sao Paulo.
    O valor e salvo como naive para manter compatibilidade com o schema atual em SQLite.
    """
    return datetime.now(BRAZIL_TIMEZONE).replace(tzinfo=None)


def serialize_brazil_datetime(value: datetime) -> str:
    """
    Serializa datetime para ISO 8601 com offset do Brasil.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=BRAZIL_TIMEZONE)
    else:
        value = value.astimezone(BRAZIL_TIMEZONE)
    return value.isoformat()
