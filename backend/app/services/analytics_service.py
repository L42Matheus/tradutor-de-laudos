"""
Persistencia de eventos epidemiologicos anonimizados.
"""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.platform_models import EpidemiologyEvent, Translation


def upsert_epidemiology_event(
    db: Session,
    *,
    translation: Translation,
    municipality: str,
    state: str,
    latitude: float,
    longitude: float,
    condition_category: str,
    age_band: str,
    event_month: Optional[date] = None,
    location_source: str = "inferred",
    source_confidence: Optional[float] = None,
) -> EpidemiologyEvent:
    existing = (
        db.query(EpidemiologyEvent)
        .filter(EpidemiologyEvent.translation_id == translation.id)
        .first()
    )

    payload = {
        "municipality": municipality,
        "state": state,
        "latitude": latitude,
        "longitude": longitude,
        "condition_category": condition_category,
        "age_band": age_band,
        "event_month": event_month or date.today().replace(day=1),
        "location_source": location_source,
        "source_confidence": source_confidence,
    }

    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
        return existing

    event = EpidemiologyEvent(translation_id=translation.id, **payload)
    db.add(event)
    return event
