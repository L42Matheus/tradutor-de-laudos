"""
Servico de validacao de documentos medicos
Garante que apenas documentos medicos sejam processados
"""

import json
import re
import unicodedata

import anthropic

from app.config import get_settings


STRICT_VALIDATION_RULES = """
Analise o {input_kind} e determine se ele e EXCLUSIVAMENTE um documento medico valido para este sistema.

Este sistema aceita SOMENTE:
- Laudos de exames (sangue, imagem, urina, biopsia, anatomopatologico, etc.)
- Resultados de exames laboratoriais
- Receitas e prescricoes medicas
- Documentos de saude mental (receitas de antidepressivos/ansioliticos e laudos psiquiatricos)

Marque como valido apenas se houver evidencia clara de contexto medico, por exemplo:
- nome de exame, biomarcadores, valores de referencia, impressao diagnostica, CID
- nome de medicamento, dosagem, posologia, CRM, assinatura ou carimbo medico
- hospital, clinica, laboratorio, medico, paciente, prescricao

Marque como invalido se for ou parecer:
- Conta de luz, agua, telefone, internet ou qualquer fatura/boleto
- Cifra, letra de musica, tablatura, partitura, acordes ou material musical
- Documento pessoal, contrato, nota fiscal, comprovante, extrato, formulario comum
- Foto pessoal, objeto, ambiente, tela, papel avulso ou qualquer conteudo sem contexto medico claro
- Qualquer documento nao relacionado a saude

Regras obrigatorias:
- Se houver duvida, pouco contexto ou ambiguidade, responda com is_valid=false.
- Nao tente reinterpretar documentos nao medicos como se fossem laudos ou receitas.
- Nao basta ter texto ou numeros; precisa ser claramente um documento medico.
- Acordes musicais como C, Dm, G7, F#m e semelhantes NUNCA sao medicamentos ou exames.
- Se contiver medicamentos para ansiedade, depressao ou outros transtornos mentais, classifique como "saude_mental".

Responda APENAS com JSON no formato:
{
    "is_valid": true ou false,
    "document_type": "laudo" ou "receita" ou "saude_mental" ou null,
    "message": "explicacao breve"
}
"""


class DocumentValidator:
    """Valida se um documento e medico (laudo ou receita)."""

    _MEDICAL_KEYWORDS = (
        "laudo", "exame", "hemograma", "hemacias", "hemoglobina", "hematocrito",
        "leucocitos", "plaquetas", "glicose", "colesterol", "biopsia", "ultrassom",
        "tomografia", "ressonancia", "radiografia", "raio x", "resultado",
        "laboratorio", "receita", "prescricao", "medicamento", "comprimido",
        "capsula", "posologia", "dosagem", "cid", "crm", "paciente", "medico",
        "clinica", "hospital", "diagnostico", "anamnese"
    )
    _UTILITY_BILL_KEYWORDS = (
        "conta de luz", "energia eletrica", "conta de energia", "consumo",
        "kwh", "unidade consumidora", "leitura anterior", "leitura atual",
        "bandeira tarifaria", "tarifa", "vencimento", "codigo de barras"
    )
    _MUSIC_KEYWORDS = (
        "cifra", "cifras", "tom:", "capotraste", "tablatura", "partitura",
        "intro", "refrao", "estrofe", "ponte", "solo", "acordes"
    )
    _CHORD_LINE_PATTERN = re.compile(
        r"^(?:[A-G](?:#|b)?(?:m|maj7|m7|7|sus2|sus4|dim|aug|add9|9|11|13)?(?:/[A-G](?:#|b)?)?\s*){2,}$",
        re.IGNORECASE
    )

    def __init__(self, api_key: str = None):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = settings.claude_model

    def validate_text(self, text: str) -> dict:
        """
        Valida se o texto e um documento medico.

        Returns:
            dict: {
                'is_valid': bool,
                'document_type': 'laudo' | 'receita' | 'saude_mental' | None,
                'message': str
            }
        """
        rejection_reason = self._get_text_rejection_reason(text)
        if rejection_reason:
            return {
                "is_valid": False,
                "document_type": None,
                "message": rejection_reason,
            }

        prompt = STRICT_VALIDATION_RULES.replace("{input_kind}", "texto") + "\n\nTEXTO PARA ANALISE:\n"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt + text[:2000]}
                ]
            )

            response_text = response.content[0].text
            return self._parse_response(response_text)

        except Exception as e:
            return {
                "is_valid": False,
                "document_type": None,
                "message": f"Erro ao validar documento: {str(e)}",
            }

    def validate_image(self, image_base64: str, media_type: str) -> dict:
        """
        Valida se a imagem e um documento medico.

        Returns:
            dict: {
                'is_valid': bool,
                'document_type': 'laudo' | 'receita' | 'saude_mental' | None,
                'message': str
            }
        """
        prompt = STRICT_VALIDATION_RULES.replace("{input_kind}", "imagem")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            response_text = response.content[0].text
            return self._parse_response(response_text)

        except Exception as e:
            return {
                "is_valid": False,
                "document_type": None,
                "message": f"Erro ao validar imagem: {str(e)}",
            }

    def _parse_response(self, response_text: str) -> dict:
        """Parse da resposta JSON do validador."""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)

            return {
                "is_valid": result.get("is_valid", False),
                "document_type": result.get("document_type"),
                "message": result.get("message", ""),
            }

        except json.JSONDecodeError:
            return {
                "is_valid": False,
                "document_type": None,
                "message": "Nao foi possivel validar o documento",
            }

    def _get_text_rejection_reason(self, text: str) -> str | None:
        """Bloqueia casos obviamente nao medicos antes de chamar o modelo."""
        normalized = self._normalize_text(text)
        medical_hits = self._count_keyword_hits(normalized, self._MEDICAL_KEYWORDS)
        utility_hits = self._count_keyword_hits(normalized, self._UTILITY_BILL_KEYWORDS)
        music_hits = self._count_keyword_hits(normalized, self._MUSIC_KEYWORDS)

        if utility_hits >= 2 and medical_hits == 0:
            return "O documento parece ser uma conta ou fatura, nao um laudo ou receita medica."

        if music_hits >= 2 and medical_hits == 0:
            return "O documento parece ser uma cifra, letra ou material musical, nao um documento medico."

        chord_lines = sum(
            1 for line in text.splitlines()
            if self._CHORD_LINE_PATTERN.fullmatch(line.strip() or "")
        )
        if chord_lines >= 2 and medical_hits == 0:
            return "O documento parece ser uma cifra com acordes musicais, nao um documento medico."

        return None

    @staticmethod
    def _count_keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        normalized = "".join(
            char for char in normalized
            if not unicodedata.combining(char)
        )
        return " ".join(normalized.lower().split())
