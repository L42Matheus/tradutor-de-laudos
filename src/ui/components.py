"""
Componentes de interface do usuario
"""

import streamlit as st
from src.config import DocumentCategory, TIPOS_LAUDO, TIPOS_RECEITA, ALLOWED_FILE_TYPES


def show_header():
    """Exibe cabecalho da aplicacao"""
    st.title("🏥 Traduz Saúde")
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


def show_footer():
    """Exibe rodape"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>🏥 Traduz Saúde</p>
        <p style='font-size: 0.8em;'>Este servico nao substitui consulta medica profissional</p>
    </div>
    """, unsafe_allow_html=True)


def show_category_selector() -> str:
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


def show_type_selector(categoria: str) -> str:
    """Exibe seletor de tipo baseado na categoria"""
    if categoria == DocumentCategory.RECEITA:
        return st.selectbox("Tipo de receita:", TIPOS_RECEITA)
    else:
        return st.selectbox("Tipo de exame:", TIPOS_LAUDO)


def show_input_method() -> str:
    """Exibe opcoes de entrada (upload ou texto)"""
    st.subheader("📤 Envie seu documento")

    return st.radio(
        "Como deseja enviar?",
        ["📁 Upload de arquivo", "✏️ Colar texto"],
        horizontal=True
    )


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


def show_text_input() -> str:
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
