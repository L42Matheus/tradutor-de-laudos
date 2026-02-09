"""
Rotas de apoio emocional
"""
from fastapi import APIRouter
import random

from app.models.responses import (
    SupportResponse,
    SupportQuote,
    BreathingExercise,
    SupportResource
)

router = APIRouter()

# Dados de apoio emocional (serão expandidos na Fase 6)
QUOTES = [
    SupportQuote(quote="Você é mais forte do que imagina. Cada passo, por menor que seja, é um avanço.", author=None),
    SupportQuote(quote="Não há vergonha em pedir ajuda. Isso é um ato de coragem, não de fraqueza.", author=None),
    SupportQuote(quote="Seus sentimentos são válidos. Permita-se senti-los sem julgamento.", author=None),
    SupportQuote(quote="A recuperação não é linear. Dias difíceis fazem parte do processo.", author=None),
    SupportQuote(quote="Você merece cuidado e compaixão, especialmente de si mesmo.", author=None),
]

EXERCISES = [
    BreathingExercise(
        name="Respiração 4-7-8",
        description="Técnica de relaxamento profundo",
        steps=[
            "Inspire pelo nariz contando até 4",
            "Segure a respiração contando até 7",
            "Expire pela boca contando até 8",
            "Repita 3-4 vezes"
        ]
    ),
    BreathingExercise(
        name="Respiração Quadrada",
        description="Técnica para acalmar a ansiedade",
        steps=[
            "Inspire contando até 4",
            "Segure contando até 4",
            "Expire contando até 4",
            "Segure contando até 4",
            "Repita 4-5 vezes"
        ]
    ),
]

RESOURCES = [
    SupportResource(
        name="CVV - Centro de Valorização da Vida",
        description="Apoio emocional e prevenção do suicídio, 24 horas",
        contact="188",
        is_emergency=True
    ),
    SupportResource(
        name="CAPS - Centro de Atenção Psicossocial",
        description="Atendimento gratuito pelo SUS",
        contact="Procure a unidade mais próxima",
        is_emergency=False
    ),
    SupportResource(
        name="UBS - Unidade Básica de Saúde",
        description="Atendimento de saúde mental na comunidade",
        contact="Procure a unidade mais próxima",
        is_emergency=False
    ),
]


@router.get("/quote", response_model=SupportQuote)
async def get_random_quote() -> SupportQuote:
    """Retorna uma frase motivacional aleatória"""
    return random.choice(QUOTES)


@router.get("/exercises", response_model=list[BreathingExercise])
async def get_exercises() -> list[BreathingExercise]:
    """Retorna lista de exercícios de respiração"""
    return EXERCISES


@router.get("/resources", response_model=list[SupportResource])
async def get_resources() -> list[SupportResource]:
    """Retorna lista de recursos de apoio"""
    return RESOURCES


@router.get("/all", response_model=SupportResponse)
async def get_all_support() -> SupportResponse:
    """Retorna todos os recursos de apoio emocional"""
    return SupportResponse(
        quotes=QUOTES,
        exercises=EXERCISES,
        resources=RESOURCES
    )
