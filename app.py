"""
Traduz Saúde
Aplicacao principal
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Carregar variaveis de ambiente do .env
APP_DIR = Path(__file__).parent.resolve()
load_dotenv(APP_DIR / '.env')

from src.config import DocumentCategory
from src.services import (
    MedicalTranslator,
    DocumentValidator,
    anonymize_text,
    can_translate,
    increment_usage,
    show_usage_status,
    show_limit_reached
)
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
    show_results,
    show_theme_toggle,
    apply_custom_styles,
    show_apoio_emocional
)

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
    apply_custom_styles()
    show_theme_toggle()
    show_usage_status()
    show_apoio_emocional()
    show_header()
    show_terms()

    consent = st.checkbox("Li e concordo com os termos acima", key="consent_checkbox")

    if not consent:
        st.warning("⚠️ Por favor, leia e aceite os termos de uso para continuar.")
        return

    # Verificar API Key (tenta st.secrets primeiro, depois .env)
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ Configuracao necessaria: adicione sua ANTHROPIC_API_KEY")
        st.info("Adicione em .streamlit/secrets.toml ou no arquivo .env")
        return

    # Inicializar servicos
    translator = MedicalTranslator(api_key)
    validator = DocumentValidator(api_key)

    # Selecao de categoria e tipo (pode ser ajustado automaticamente)
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
                # Salva file_data processado no session_state
                st.session_state.processed_file_data = file_data
        elif st.session_state.get('uploaded_file_data'):
            # Usa arquivo salvo no session_state (apos mudar tema)
            file_data = st.session_state.get('processed_file_data')
    else:
        texto = show_text_input()
        # Limpa arquivo do session_state se mudou para texto
        if 'uploaded_file_data' in st.session_state:
            del st.session_state.uploaded_file_data
        if 'processed_file_data' in st.session_state:
            del st.session_state.processed_file_data

    # Botao de traducao
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        traduzir_btn = st.button("🔄 Traduzir Documento", use_container_width=True, type="primary")

    has_content = file_data or (texto and texto.strip())

    if traduzir_btn and has_content:
        if not can_translate():
            show_limit_reached()
            return

        with st.spinner("Validando documento... ⏳"):
            validation = validate_document(validator, file_data, texto)

            if not validation['is_valid']:
                st.error(f"❌ Documento nao aceito: {validation['message']}")
                st.warning("Este sistema aceita apenas laudos medicos e receitas. "
                          "Documentos como contas de luz, agua, boletos, etc. nao sao processados.")
                return

            st.success(f"✅ Documento validado: {validation['message']}")

            # Verifica se categoria selecionada corresponde ao documento detectado
            detected_type = validation.get('document_type')
            if detected_type:
                detected_type = detected_type.lower()
                if detected_type != categoria:
                    if detected_type == "saude_mental":
                        tipo_nome = "Ansiedade/Depressão"
                        tipo = "Outro"
                    elif detected_type == "receita":
                        tipo_nome = "Receita Médica"
                        tipo = "Receita Simples"
                    else:
                        tipo_nome = "Laudo Médico"
                        tipo = "Outro"
                    st.info(f"📋 Documento detectado como **{tipo_nome}**. Ajustando automaticamente.")
                    categoria = detected_type

        with st.spinner("Traduzindo documento... ⏳"):
            try:
                resultado = process_document(translator, file_data, texto, tipo, categoria)

                if resultado:
                    if not resultado.get('from_cache'):
                        increment_usage()
                    st.session_state.resultado = resultado
                    st.session_state.resultado_categoria = categoria
                    show_results(resultado, categoria)
                else:
                    st.error("❌ Nao foi possivel processar o documento")

            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")
                st.info("Tente novamente ou entre em contato com o suporte.")

    elif traduzir_btn and not has_content:
        st.warning("⚠️ Por favor, envie um arquivo ou cole o texto do documento antes de traduzir.")

    # Mostra resultado salvo (apos mudar tema)
    elif st.session_state.get('resultado') and has_content:
        show_results(st.session_state.resultado, st.session_state.resultado_categoria)


if __name__ == "__main__":
    main()
    show_footer()
