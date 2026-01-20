"""
Interface Streamlit para o Tradutor de Documentos Medicos
Suporta laudos e receitas medicas
"""

import streamlit as st
import os
from dotenv import load_dotenv

from config import DocumentCategory, TIPOS_LAUDO, TIPOS_RECEITA, ALLOWED_FILE_TYPES
from translator import MedicalTranslator
from validators import DocumentValidator
from anonymizer import anonymize_text
from file_reader import process_uploaded_file

# Carregar variaveis de ambiente
load_dotenv()

# Configuracao da pagina
st.set_page_config(
    page_title="Tradutor de Documentos Medicos",
    page_icon="🏥",
    layout="wide"
)


def show_header():
    """Exibe cabecalho da aplicacao"""
    st.title("🏥 Tradutor de Documentos Medicos")
    st.markdown("*Entenda seus exames e receitas de forma simples e clara*")


def show_terms():
    """Exibe termos de uso"""
    with st.expander("⚠️ IMPORTANTE: Leia antes de usar", expanded=False):
        st.markdown("""
        ### Termos de Uso e Privacidade

        ✅ **Seus dados estao seguros:**
        - Nao armazenamos nenhum documento ou informacao pessoal
        - Dados pessoais sao automaticamente removidos antes do processamento
        - Tudo e processado em memoria e descartado apos a traducao

        ⚠️ **Este servico NAO substitui consulta medica:**
        - Use apenas para melhor compreensao dos seus documentos
        - Sempre consulte seu medico para interpretacao oficial
        - Em caso de duvidas, procure um profissional de saude

        📋 **LGPD:**
        - Seus dados sao processados de forma anonima
        - Nao compartilhamos informacoes com terceiros
        """)


def show_category_selector():
    """Exibe seletor de categoria (laudo ou receita)"""
    st.subheader("📋 O que voce deseja traduzir?")

    categoria = st.radio(
        "Selecione o tipo de documento:",
        ["📄 Laudo Medico", "💊 Receita Medica"],
        horizontal=True
    )

    if "Laudo" in categoria:
        return DocumentCategory.LAUDO
    else:
        return DocumentCategory.RECEITA


def show_type_selector(categoria: str):
    """Exibe seletor de tipo baseado na categoria"""
    if categoria == DocumentCategory.RECEITA:
        return st.selectbox("Tipo de receita:", TIPOS_RECEITA)
    else:
        return st.selectbox("Tipo de exame:", TIPOS_LAUDO)


def show_input_method():
    """Exibe opcoes de entrada (upload ou texto)"""
    st.subheader("📤 Envie seu documento")

    input_method = st.radio(
        "Como deseja enviar?",
        ["📁 Upload de arquivo", "✏️ Colar texto"],
        horizontal=True
    )

    return input_method


def show_file_uploader():
    """Exibe componente de upload de arquivo"""
    st.markdown("Formatos aceitos: **PDF**, **Imagem** (JPG, PNG) ou **Texto** (TXT)")

    uploaded_file = st.file_uploader(
        "Escolha o arquivo",
        type=ALLOWED_FILE_TYPES,
        help="Envie o arquivo do seu documento medico."
    )

    if uploaded_file:
        file_details = f"**Arquivo:** {uploaded_file.name} | **Tamanho:** {uploaded_file.size / 1024:.1f} KB"
        st.caption(file_details)

        if uploaded_file.type.startswith('image/'):
            st.image(uploaded_file, caption="Preview do documento", use_container_width=True)
            uploaded_file.seek(0)

    return uploaded_file


def show_text_input():
    """Exibe area de texto para colar documento"""
    return st.text_area(
        "Cole o texto do documento:",
        height=300,
        placeholder="Cole aqui o texto do seu documento medico..."
    )


def show_results(resultado: dict, categoria: str):
    """Exibe resultados da traducao"""
    st.success("✅ Traducao concluida!")

    # Labels baseados na categoria
    if categoria == DocumentCategory.RECEITA:
        tab_labels = ["💊 Resumo", "📋 Como Tomar", "📚 Termos"]
    else:
        tab_labels = ["📋 Resumo Simples", "🔍 Explicacao Detalhada", "📚 Termos Tecnicos"]

    tab1, tab2, tab3 = st.tabs(tab_labels)

    with tab1:
        st.markdown("### " + tab_labels[0].split(" ", 1)[1])
        st.markdown(resultado.get('resumo', 'Nao disponivel'))

    with tab2:
        st.markdown("### " + tab_labels[1].split(" ", 1)[1])
        st.markdown(resultado.get('detalhado', 'Nao disponivel'))

    with tab3:
        st.markdown("### Glossario")
        st.markdown(resultado.get('glossario', 'Nao disponivel'))

    if resultado.get('alertas'):
        st.warning("⚠️ " + resultado['alertas'])

    st.info("💡 **Lembre-se:** Esta traducao e apenas informativa. Sempre consulte seu medico!")


def validate_document(validator: DocumentValidator, file_data: dict, laudo_texto: str) -> dict:
    """Valida se o documento e medico"""
    if laudo_texto and laudo_texto.strip():
        return validator.validate_text(laudo_texto)
    elif file_data:
        if file_data['type'] == 'image':
            return validator.validate_image(file_data['content'], file_data['media_type'])
        elif file_data['type'] == 'text':
            return validator.validate_text(file_data['content'])
    return {'is_valid': False, 'message': 'Nenhum documento para validar'}


def process_document(translator: MedicalTranslator, file_data: dict, laudo_texto: str,
                    tipo: str, categoria: str) -> dict:
    """Processa e traduz o documento"""
    if laudo_texto and laudo_texto.strip():
        laudo_anonimizado, dados_removidos = anonymize_text(laudo_texto)
        if dados_removidos:
            st.info(f"🔒 Dados pessoais removidos: {', '.join(dados_removidos)}")
        return translator.translate_text(laudo_anonimizado, tipo, categoria)

    elif file_data:
        if file_data['type'] == 'text':
            laudo_anonimizado, dados_removidos = anonymize_text(file_data['content'])
            if dados_removidos:
                st.info(f"🔒 Dados pessoais removidos: {', '.join(dados_removidos)}")
            return translator.translate_text(laudo_anonimizado, tipo, categoria)

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
    laudo_texto = None
    file_data = None

    if "Upload" in input_method:
        uploaded_file = show_file_uploader()
        if uploaded_file:
            file_data = process_uploaded_file(uploaded_file)
            if file_data.get('error'):
                st.error(f"❌ {file_data['error']}")
                file_data = None
    else:
        laudo_texto = show_text_input()

    # Botao de traducao
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        traduzir_btn = st.button("🔄 Traduzir Documento", use_container_width=True, type="primary")

    has_content = file_data or (laudo_texto and laudo_texto.strip())

    if traduzir_btn and has_content:
        with st.spinner("Validando documento... ⏳"):
            # Validar se e documento medico
            validation = validate_document(validator, file_data, laudo_texto)

            if not validation['is_valid']:
                st.error(f"❌ Documento nao aceito: {validation['message']}")
                st.warning("Este sistema aceita apenas laudos medicos e receitas. "
                          "Documentos como contas de luz, agua, boletos, etc. nao sao processados.")
                return

            st.success(f"✅ Documento validado: {validation['message']}")

        with st.spinner("Traduzindo documento... ⏳"):
            try:
                resultado = process_document(translator, file_data, laudo_texto, tipo, categoria)

                if resultado:
                    show_results(resultado, categoria)
                else:
                    st.error("❌ Nao foi possivel processar o documento")

            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")
                st.info("Tente novamente ou entre em contato com o suporte.")

    elif traduzir_btn and not has_content:
        st.warning("⚠️ Por favor, envie um arquivo ou cole o texto do documento antes de traduzir.")


def show_footer():
    """Exibe rodape"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>🏥 Tradutor de Documentos Medicos</p>
        <p style='font-size: 0.8em;'>Este servico nao substitui consulta medica profissional</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    show_footer()
