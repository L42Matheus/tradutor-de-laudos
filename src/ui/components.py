"""
Componentes de interface do usuario
"""

import streamlit as st
from src.config import DocumentCategory, TIPOS_LAUDO, TIPOS_RECEITA, ALLOWED_FILE_TYPES
from src.ui.styles import get_custom_css, get_header_html, get_footer_html


def init_theme():
    """Inicializa o estado do tema"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'


def _on_theme_change():
    """Callback quando tema muda"""
    selected = st.session_state.theme_select
    st.session_state.theme = 'dark' if selected == "Escuro" else 'light'


def show_theme_toggle():
    """Exibe toggle para alternar entre tema claro e escuro na sidebar"""
    with st.sidebar:
        st.markdown("### Configuracoes")
        current_theme = st.session_state.get('theme', 'dark')

        theme_options = ["Escuro", "Claro"]
        current_index = 0 if current_theme == 'dark' else 1

        st.selectbox(
            "Tema:",
            theme_options,
            index=current_index,
            key="theme_select",
            on_change=_on_theme_change
        )


def apply_custom_styles():
    """Aplica estilos CSS customizados baseados no tema atual"""
    init_theme()
    theme = st.session_state.get('theme', 'dark')
    st.markdown(get_custom_css(theme), unsafe_allow_html=True)


def show_header():
    """Exibe cabecalho da aplicacao"""
    st.markdown(get_header_html(), unsafe_allow_html=True)


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
    st.markdown(get_footer_html(), unsafe_allow_html=True)


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
        help="Envie o arquivo do seu documento medico.",
        key="file_uploader"
    )

    # Salva no session_state quando faz upload
    if uploaded_file:
        st.session_state.uploaded_file_data = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'content': uploaded_file.getvalue()
        }
        uploaded_file.seek(0)

    # Mostra preview se tem arquivo (atual ou salvo)
    file_data = st.session_state.get('uploaded_file_data')
    if uploaded_file:
        file_details = f"**Arquivo:** {uploaded_file.name} | **Tamanho:** {uploaded_file.size / 1024:.1f} KB"
        st.caption(file_details)

        if uploaded_file.type.startswith('image/'):
            st.image(uploaded_file, caption="Preview do documento", use_container_width=True)
            uploaded_file.seek(0)
    elif file_data:
        file_details = f"**Arquivo:** {file_data['name']} | **Tamanho:** {file_data['size'] / 1024:.1f} KB"
        st.caption(file_details)

        if file_data['type'].startswith('image/'):
            st.image(file_data['content'], caption="Preview do documento", use_container_width=True)

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
    # Indicador de cache
    if resultado.get('from_cache'):
        st.success("✅ Traducao concluida! (recuperado do cache)")
    else:
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
        _show_copy_button(resultado.get('resumo', ''), "resumo")

    with tab2:
        st.markdown("### " + tab_labels[1].split(" ", 1)[1])
        st.markdown(resultado.get('detalhado', 'Nao disponivel'))
        _show_copy_button(resultado.get('detalhado', ''), "detalhado")

    with tab3:
        st.markdown("### Glossario")
        st.markdown(resultado.get('glossario', 'Nao disponivel'))
        _show_copy_button(resultado.get('glossario', ''), "glossario")

    if resultado.get('alertas'):
        st.warning("⚠️ " + resultado['alertas'])

    # Botao copiar tudo
    _show_copy_all_button(resultado)

    st.info("💡 **Lembre-se:** Esta traducao e apenas informativa. Sempre consulte seu medico!")


def _show_copy_button(text: str, key: str):
    """Exibe botao para copiar texto especifico"""
    if st.button(f"📋 Copiar", key=f"copy_{key}", use_container_width=False):
        st.code(text, language=None)
        st.caption("Texto acima pronto para copiar (Ctrl+C)")


def _show_copy_all_button(resultado: dict):
    """Exibe botao para copiar todo o resultado"""
    full_text = f"""RESUMO:
{resultado.get('resumo', '')}

DETALHADO:
{resultado.get('detalhado', '')}

GLOSSARIO:
{resultado.get('glossario', '')}
"""
    if resultado.get('alertas'):
        full_text += f"\nALERTAS:\n{resultado['alertas']}"

    with st.expander("📋 Copiar resultado completo"):
        st.code(full_text, language=None)
        st.caption("Selecione todo o texto acima e copie (Ctrl+A, Ctrl+C)")
