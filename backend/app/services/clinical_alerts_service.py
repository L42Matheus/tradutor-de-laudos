"""
Alertas clÃ­nicos determinÃ­sticos e alertas oriundos do modelo.

Para saÃºde, alertas crÃ­ticos nÃ£o podem depender apenas do LLM.
"""
import unicodedata
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AlertCandidate:
    source_type: str
    severity: str
    title: str
    message: str
    requires_urgent_care: bool = False
    code: Optional[str] = None


@dataclass(frozen=True)
class DeterministicRule:
    code: str
    severity: str
    title: str
    requires_urgent_care: bool
    groups: tuple[tuple[str, ...], ...]
    message: str


CRITICAL_RULES: tuple[DeterministicRule, ...] = (
    DeterministicRule(
        code="neuro_mass_effect",
        severity="critical",
        title="Achado neurologico grave",
        requires_urgent_care=True,
        groups=(
            ("cerebr", "cranio", "intracran", "frontopariet", "frontal", "parietal", "temporal", "occipital"),
            ("lesao expansiva", "massa", "tumor", "nodulo expansivo"),
            ("edema", "compress", "efeito de massa", "desvio", "deslocamento", "linha media", "ventriculo", "hernia"),
        ),
        message=(
            "Este exame sugere um achado cerebral importante com pressao sobre estruturas do cerebro e "
            "requer avaliacao medica urgente, idealmente neurologica ou neurocirurgica."
        ),
    ),
    DeterministicRule(
        code="neuro_hemorrhage",
        severity="critical",
        title="Possivel sangramento neurologico",
        requires_urgent_care=True,
        groups=(
            ("cerebr", "cranio", "intracran"),
            ("hemorrag", "hematoma", "sangramento"),
        ),
        message="Ha indicio de sangramento em contexto neurologico. Isso exige avaliacao medica urgente.",
    ),
    DeterministicRule(
        code="acute_stroke",
        severity="critical",
        title="Possivel evento neurologico agudo",
        requires_urgent_care=True,
        groups=(
            ("avc", "isquemi", "infarto cerebral", "oclusao", "trombo"),
            ("agud", "recente", "territorio"),
        ),
        message=(
            "O exame pode indicar um evento neurologico agudo. Se houver perda de forca, fala alterada, "
            "assimetria facial ou confusao, procure atendimento de urgencia."
        ),
    ),
    DeterministicRule(
        code="pulmonary_urgent",
        severity="high",
        title="Achado toracico potencialmente grave",
        requires_urgent_care=True,
        groups=(
            ("pulm", "torax", "pleur"),
            ("embolia", "pneumotorax", "derrame pleural volumoso", "insuficiencia respiratoria"),
        ),
        message=(
            "Ha um achado toracico potencialmente grave. Se houver falta de ar, dor no peito ou piora rapida, "
            "procure atendimento de urgencia."
        ),
    ),
    DeterministicRule(
        code="cardiovascular_urgent",
        severity="high",
        title="Achado cardiovascular potencialmente grave",
        requires_urgent_care=True,
        groups=(
            ("aorta", "cardi", "coronar", "miocard", "vascular"),
            ("dissecc", "aneurisma", "oclusao", "infarto", "trombo"),
        ),
        message="O exame descreve um achado cardiovascular potencialmente grave que precisa de avaliacao medica urgente.",
    ),
)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def derive_alert_candidates(original_text: str, result_payload: dict) -> list[AlertCandidate]:
    alerts: list[AlertCandidate] = []
    normalized_text = normalize_text(original_text)

    for rule in CRITICAL_RULES:
        if all(any(token in normalized_text for token in group) for group in rule.groups):
            alerts.append(
                AlertCandidate(
                    source_type="regra",
                    severity=rule.severity,
                    title=rule.title,
                    message=rule.message,
                    requires_urgent_care=rule.requires_urgent_care,
                    code=rule.code,
                )
            )

    model_alerts = result_payload.get("alertas", []) or []
    for message in model_alerts:
        if not isinstance(message, str) or not message.strip():
            continue
        alerts.append(
            AlertCandidate(
                source_type="modelo",
                severity="warning",
                title="Alerta do modelo",
                message=message.strip(),
                requires_urgent_care="urgen" in normalize_text(message),
            )
        )

    deduped: list[AlertCandidate] = []
    seen_messages: set[str] = set()
    for alert in alerts:
        key = normalize_text(alert.message)
        if key in seen_messages:
            continue
        seen_messages.add(key)
        deduped.append(alert)

    return deduped


def merge_alert_texts(original_text: str, result_payload: dict) -> list[str]:
    return [alert.message for alert in derive_alert_candidates(original_text, result_payload)]
