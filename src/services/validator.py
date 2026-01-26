"""
Servico de validacao de documentos medicos
Garante que apenas documentos medicos sejam processados
"""

import json
import anthropic

from src.config import CLAUDE_MODEL


class DocumentValidator:
    """Valida se um documento e medico (laudo ou receita)"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = CLAUDE_MODEL

    def validate_text(self, text: str) -> dict:
        """
        Valida se o texto e um documento medico

        Args:
            text: Texto do documento

        Returns:
            dict: {
                'is_valid': bool,
                'document_type': 'laudo' | 'receita' | None,
                'message': str
            }
        """
        prompt = """Analise o texto abaixo e determine se e um documento medico valido.

Documentos ACEITOS:
- Laudos de exames (sangue, imagem, urina, biopsia, etc)
- Receitas medicas
- Resultados de exames laboratoriais
- Laudos de ultrassom, raio-x, tomografia, ressonancia
- Prescricoes medicas
- Receitas/laudos de saude mental (antidepressivos, ansioliticos, psiquiatria)

Documentos NAO ACEITOS:
- Contas de luz, agua, telefone
- Boletos bancarios
- Documentos pessoais (RG, CPF, CNH)
- Contratos
- Notas fiscais
- Qualquer documento nao relacionado a saude

IMPORTANTE: Se o documento contem medicamentos para ansiedade, depressao ou outros transtornos mentais (antidepressivos, ansioliticos, antipsicoticos, estabilizadores de humor), classifique como "saude_mental".

Responda APENAS com JSON no formato:
{
    "is_valid": true ou false,
    "document_type": "laudo" ou "receita" ou "saude_mental" ou null,
    "message": "explicacao breve"
}

TEXTO PARA ANALISE:
"""

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
                'is_valid': False,
                'document_type': None,
                'message': f'Erro ao validar documento: {str(e)}'
            }

    def validate_image(self, image_base64: str, media_type: str) -> dict:
        """
        Valida se a imagem e um documento medico

        Args:
            image_base64: Imagem em base64
            media_type: Tipo MIME da imagem

        Returns:
            dict: {
                'is_valid': bool,
                'document_type': 'laudo' | 'receita' | None,
                'message': str
            }
        """
        prompt = """Analise a imagem e determine se e um documento medico valido.

Documentos ACEITOS:
- Laudos de exames (sangue, imagem, urina, biopsia, etc)
- Receitas medicas
- Resultados de exames laboratoriais
- Laudos de ultrassom, raio-x, tomografia, ressonancia
- Prescricoes medicas
- Receitas/laudos de saude mental (antidepressivos, ansioliticos, psiquiatria)

Documentos NAO ACEITOS:
- Contas de luz, agua, telefone
- Boletos bancarios
- Documentos pessoais (RG, CPF, CNH)
- Contratos
- Notas fiscais
- Fotos pessoais
- Qualquer documento nao relacionado a saude

IMPORTANTE: Se o documento contem medicamentos para ansiedade, depressao ou outros transtornos mentais (antidepressivos, ansioliticos, antipsicoticos, estabilizadores de humor), classifique como "saude_mental".

Responda APENAS com JSON no formato:
{
    "is_valid": true ou false,
    "document_type": "laudo" ou "receita" ou "saude_mental" ou null,
    "message": "explicacao breve"
}"""

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
                'is_valid': False,
                'document_type': None,
                'message': f'Erro ao validar imagem: {str(e)}'
            }

    def _parse_response(self, response_text: str) -> dict:
        """Parse da resposta JSON do validador"""
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
                'is_valid': result.get('is_valid', False),
                'document_type': result.get('document_type'),
                'message': result.get('message', '')
            }

        except json.JSONDecodeError:
            return {
                'is_valid': False,
                'document_type': None,
                'message': 'Nao foi possivel validar o documento'
            }
