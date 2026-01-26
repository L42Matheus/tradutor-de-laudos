"""
Servico de limite de uso para modelo freemium
"""

import streamlit as st
from src.config import FREE_TRANSLATIONS_LIMIT


def init_usage_tracking():
    if 'translations_count' not in st.session_state:
        st.session_state.translations_count = 0


def get_remaining_translations() -> int:
    init_usage_tracking()
    return max(0, FREE_TRANSLATIONS_LIMIT - st.session_state.translations_count)


def can_translate() -> bool:
    init_usage_tracking()
    return st.session_state.translations_count < FREE_TRANSLATIONS_LIMIT


def increment_usage():
    init_usage_tracking()
    st.session_state.translations_count += 1


def show_usage_status():
    remaining = get_remaining_translations()
    total = FREE_TRANSLATIONS_LIMIT
    st.sidebar.markdown(f"**Traducoes gratuitas:** {remaining}/{total}")
    st.sidebar.progress(remaining / total if remaining > 0 else 0)


def show_limit_reached():
    st.warning("🔒 **Limite de traducoes gratuitas atingido!**")

    st.markdown("""
    ### Voce usou suas traducoes gratuitas

    Para continuar, crie sua conta:

    - ✅ Traducoes ilimitadas
    - ✅ Historico de traducoes
    - ✅ Suporte prioritario
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.button("📧 Criar Conta", type="primary", use_container_width=True)
    with col2:
        st.button("🔑 Ja tenho conta", use_container_width=True)

    st.caption("*Em breve: planos a partir de R$ 9,90/mes*")
