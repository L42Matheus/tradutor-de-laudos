"""
Traduz Saúde
Aplicacao principal
"""

import streamlit as st
import os
from dotenv import load_dotenv

from src.config import DocumentCategory
from src.services import MedicalTranslator, DocumentValidator, anonymize_text
from src.utils import process_uploaded_file
from src.ui import (
    show_header,
    show_terms,
    show_footer,
    show_category_selector,
    show_type_selector,
    show_input_method,
    show_file_uploader,
    show_text_input,
    show_results
)

# Carregar variaveis de ambiente
load_dotenv()

# Configuracao da pagina
st.set_page_config(
    page_title="Traduz Saúde",
    page_icon="🏥",
    layout="wide"
)


def validate_document(validator: DocumentValidator, file_data: dict, texto: str) -> dict:
    """Valida se o documento e medico"""
    if texto and texto.strip():
        return validator.validate_text(texto)
    elif file_data:
        if file_data['type'] == 'image':
            return validator.validate_image(file_data['content'], file_data['media_type'])
        elif file_data['type'] == 'text':
            return validator.validate_text(file_data['content'])
    return {'is_valid': False, 'message': 'Nenhum documento para validar'}


def process_document(translator: MedicalTranslator, file_data: dict, texto: str,
                    tipo: str, categoria: str) -> dict:
    """Processa e traduz o documento"""
    if texto and texto.strip():
        texto_anonimizado, dados_removidos = anonymize_text(texto)
        if dados_removidos:
            st.info(f"🔒 Dados pessoais removidos: {', '.join(dados_removidos)}")
        return translator.translate_text(texto_anonimizado, tipo, categoria)

    elif file_data:
        if file_data['type'] == 'text':
            texto_anonimizado, dados_removidos = anonymize_text(file_data['content'])
            if dados_removidos:
                st.info(f"🔒 Dados pessoais removidos: {', '.join(dados_removidos)}")
            return translator.translate_text(texto_anonimizado, tipo, categoria)

        elif file_data['type'] == 'image':
            st.info("🖼️ Processando imagem...")
            return translator.translate_image(
                file_data['content'],
                file_data['media_type'],
                tipo,
                categoria
            )

    return None


def main():
    """Funcao principal da aplicacao"""
    show_header()
    show_terms()

    consent = st.checkbox("Li e concordo com os termos acima")

    if not consent:
        st.warning("⚠️ Por favor, leia e aceite os termos de uso para continuar.")
        return

    # Verificar API Key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ Configuracao necessaria: adicione sua ANTHROPIC_API_KEY no arquivo .env")
        st.info("Veja o arquivo .env.example para instrucoes")
        return

    # Inicializar servicos
    translator = MedicalTranslator(api_key)
    validator = DocumentValidator(api_key)

    # Selecao de categoria e tipo
    categoria = show_category_selector()
    tipo = show_type_selector(categoria)

    # Metodo de entrada
    input_method = show_input_method()

    uploaded_file = None
    texto = None
    file_data = None

    if "Upload" in input_method:
        uploaded_file = show_file_uploader()
        if uploaded_file:
            file_data = process_uploaded_file(uploaded_file)
            if file_data.get('error'):
                st.error(f"❌ {file_data['error']}")
                file_data = None
    else:
        texto = show_text_input()

    # Botao de traducao
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        traduzir_btn = st.button("🔄 Traduzir Documento", use_container_width=True, type="primary")

    has_content = file_data or (texto and texto.strip())

    if traduzir_btn and has_content:
        with st.spinner("Validando documento... ⏳"):
            validation = validate_document(validator, file_data, texto)

            if not validation['is_valid']:
                st.error(f"❌ Documento nao aceito: {validation['message']}")
                st.warning("Este sistema aceita apenas laudos medicos e receitas. "
                          "Documentos como contas de luz, agua, boletos, etc. nao sao processados.")
                return

            st.success(f"✅ Documento validado: {validation['message']}")

        with st.spinner("Traduzindo documento... ⏳"):
            try:
                resultado = process_document(translator, file_data, texto, tipo, categoria)

                if resultado:
                    show_results(resultado, categoria)
                else:
                    st.error("❌ Nao foi possivel processar o documento")

            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")
                st.info("Tente novamente ou entre em contato com o suporte.")

    elif traduzir_btn and not has_content:
        st.warning("⚠️ Por favor, envie um arquivo ou cole o texto do documento antes de traduzir.")


if __name__ == "__main__":
    main()
    show_footer()
