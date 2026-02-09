"""
Testes do sistema de prompts
"""
import pytest
from app.prompts import get_prompt_by_type
from app.prompts.laudos import (
    PROMPT_EXAME_SANGUE,
    PROMPT_EXAME_IMAGEM,
    PROMPT_EXAME_URINA,
    PROMPT_BIOPSIA,
    PROMPT_LAUDO_OUTROS
)
from app.prompts.receitas import (
    PROMPT_RECEITA_SIMPLES,
    PROMPT_RECEITA_CONTROLADA,
    PROMPT_RECEITA_ANTIBIOTICO
)
from app.prompts.saude_mental import (
    PROMPT_ANTIDEPRESSIVO,
    PROMPT_ANSIOLITICO,
    PROMPT_LAUDO_PSIQUIATRICO,
    PROMPT_SAUDE_MENTAL_OUTROS
)
from app.models.enums import DocumentCategory


class TestPromptSelector:
    """Testes do seletor de prompts"""

    def test_get_laudo_exame_sangue(self):
        """Testa prompt para exame de sangue"""
        prompt = get_prompt_by_type("exame_sangue", DocumentCategory.LAUDO)
        assert prompt == PROMPT_EXAME_SANGUE
        assert "EXAMES DE SANGUE" in prompt

    def test_get_laudo_exame_imagem(self):
        """Testa prompt para exame de imagem"""
        prompt = get_prompt_by_type("exame_imagem", DocumentCategory.LAUDO)
        assert prompt == PROMPT_EXAME_IMAGEM
        assert "EXAMES DE IMAGEM" in prompt

    def test_get_laudo_exame_urina(self):
        """Testa prompt para exame de urina"""
        prompt = get_prompt_by_type("exame_urina", DocumentCategory.LAUDO)
        assert prompt == PROMPT_EXAME_URINA
        assert "EXAMES DE URINA" in prompt

    def test_get_laudo_biopsia(self):
        """Testa prompt para biópsia"""
        prompt = get_prompt_by_type("biopsia", DocumentCategory.LAUDO)
        assert prompt == PROMPT_BIOPSIA
        assert "BIOPSIAS" in prompt

    def test_get_laudo_outros(self):
        """Testa prompt para outros laudos"""
        prompt = get_prompt_by_type("outros", DocumentCategory.LAUDO)
        assert prompt == PROMPT_LAUDO_OUTROS

    def test_get_receita_simples(self):
        """Testa prompt para receita simples"""
        prompt = get_prompt_by_type("simples", DocumentCategory.RECEITA)
        assert prompt == PROMPT_RECEITA_SIMPLES
        assert "RECEITAS SIMPLES" in prompt

    def test_get_receita_controlada(self):
        """Testa prompt para receita controlada"""
        prompt = get_prompt_by_type("controlada", DocumentCategory.RECEITA)
        assert prompt == PROMPT_RECEITA_CONTROLADA
        assert "CONTROLE ESPECIAL" in prompt

    def test_get_receita_antibiotico(self):
        """Testa prompt para receita de antibiótico"""
        prompt = get_prompt_by_type("antibiotico", DocumentCategory.RECEITA)
        assert prompt == PROMPT_RECEITA_ANTIBIOTICO
        assert "ANTIBIOTICO" in prompt

    def test_get_saude_mental_antidepressivo(self):
        """Testa prompt para antidepressivo"""
        prompt = get_prompt_by_type("antidepressivo", DocumentCategory.SAUDE_MENTAL)
        assert prompt == PROMPT_ANTIDEPRESSIVO
        assert "antidepressivo" in prompt.lower()

    def test_get_saude_mental_ansiolitico(self):
        """Testa prompt para ansiolítico"""
        prompt = get_prompt_by_type("ansiolitico", DocumentCategory.SAUDE_MENTAL)
        assert prompt == PROMPT_ANSIOLITICO
        assert "ansiolitico" in prompt.lower()

    def test_get_saude_mental_laudo_psiquiatrico(self):
        """Testa prompt para laudo psiquiátrico"""
        prompt = get_prompt_by_type("laudo_psiquiatrico", DocumentCategory.SAUDE_MENTAL)
        assert prompt == PROMPT_LAUDO_PSIQUIATRICO
        assert "psiquiatrico" in prompt.lower()

    def test_get_unknown_type_returns_default(self):
        """Testa que tipo desconhecido retorna prompt padrão"""
        prompt = get_prompt_by_type("tipo_inexistente", DocumentCategory.LAUDO)
        assert prompt == PROMPT_LAUDO_OUTROS


class TestPromptContent:
    """Testes do conteúdo dos prompts"""

    def test_laudo_prompts_contain_educational_disclaimer(self):
        """Testa que prompts de laudo contêm aviso educacional"""
        prompts = [PROMPT_EXAME_SANGUE, PROMPT_EXAME_IMAGEM, PROMPT_EXAME_URINA, PROMPT_BIOPSIA]
        for prompt in prompts:
            assert "EDUCACIONAL" in prompt

    def test_receita_prompts_contain_educational_disclaimer(self):
        """Testa que prompts de receita contêm aviso educacional"""
        prompts = [PROMPT_RECEITA_SIMPLES, PROMPT_RECEITA_CONTROLADA, PROMPT_RECEITA_ANTIBIOTICO]
        for prompt in prompts:
            assert "EDUCACIONAL" in prompt

    def test_saude_mental_prompts_are_empathetic(self):
        """Testa que prompts de saúde mental são empáticos"""
        prompts = [PROMPT_ANTIDEPRESSIVO, PROMPT_ANSIOLITICO, PROMPT_LAUDO_PSIQUIATRICO]
        for prompt in prompts:
            assert "acolhedora" in prompt.lower() or "empático" in prompt.lower()

    def test_biopsia_prompt_is_careful(self):
        """Testa que prompt de biópsia é cuidadoso"""
        assert "EXTREMAMENTE cuidadoso" in PROMPT_BIOPSIA
        assert "empatico" in PROMPT_BIOPSIA.lower()
