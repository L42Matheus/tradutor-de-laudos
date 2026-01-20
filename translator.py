import anthropic
from prompts import get_prompt_by_type

class LaudoTranslator:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def _get_user_prompt(self):
        """Retorna o prompt padrão para análise de laudos"""
        return """Por favor, forneça:
1. Um resumo em linguagem muito simples (como se explicasse para alguém sem conhecimento médico)
2. Uma explicação mais detalhada de cada parte importante
3. Um glossário dos principais termos técnicos encontrados
4. Alertas caso haja algo que exija atenção médica urgente

Formato da resposta em JSON:
{
    "resumo": "texto do resumo simples",
    "detalhado": "explicação detalhada",
    "glossario": "glossário de termos",
    "alertas": "avisos importantes ou null"
}"""

    def translate(self, laudo_text, tipo_exame):
        """
        Traduz um laudo médico para linguagem simples

        Args:
            laudo_text: Texto do laudo (já anonimizado)
            tipo_exame: Tipo do exame médico

        Returns:
            dict com resumo, explicação detalhada, glossário e alertas
        """

        system_prompt = get_prompt_by_type(tipo_exame)

        user_message = f"""Analise o seguinte laudo médico e forneça uma explicação completa:

{laudo_text}

{self._get_user_prompt()}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = response.content[0].text
            resultado = self._parse_response(response_text)

            return resultado

        except Exception as e:
            raise Exception(f"Erro ao processar com a API: {str(e)}")

    def translate_image(self, image_base64, media_type, tipo_exame):
        """
        Traduz um laudo médico a partir de uma imagem

        Args:
            image_base64: Imagem em base64
            media_type: Tipo MIME da imagem (ex: image/jpeg)
            tipo_exame: Tipo do exame médico

        Returns:
            dict com resumo, explicação detalhada, glossário e alertas
        """

        system_prompt = get_prompt_by_type(tipo_exame)

        user_content = [
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
                "text": f"""Analise a imagem do laudo médico acima e forneça uma explicação completa.

{self._get_user_prompt()}"""
            }
        ]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_content}
                ]
            )

            response_text = response.content[0].text
            resultado = self._parse_response(response_text)

            return resultado

        except Exception as e:
            raise Exception(f"Erro ao processar imagem com a API: {str(e)}")
    
    def _parse_response(self, response_text):
        """
        Faz parse da resposta do Claude
        Versão simplificada - em produção, use json.loads
        """
        import json
        
        try:
            # Tentar extrair JSON da resposta
            # Claude às vezes retorna com ```json ... ```
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text
            
            resultado = json.loads(json_text)
            
            # Garantir que todos os campos existem
            return {
                'resumo': resultado.get('resumo', 'Não foi possível gerar resumo'),
                'detalhado': resultado.get('detalhado', 'Não foi possível gerar explicação detalhada'),
                'glossario': resultado.get('glossario', 'Não foi possível gerar glossário'),
                'alertas': resultado.get('alertas', None)
            }
            
        except json.JSONDecodeError:
            # Se falhar o parse, retornar resposta raw de forma estruturada
            return {
                'resumo': response_text[:500] + "...",
                'detalhado': response_text,
                'glossario': "Não foi possível gerar glossário",
                'alertas': None
            }
