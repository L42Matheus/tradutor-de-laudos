"""
Componente de apoio emocional
"""

import random
import streamlit as st


FRASES_MOTIVACIONAIS = [
    "Voce e mais forte do que imagina. Um dia de cada vez.",
    "Nao ha vergonha em pedir ajuda. Isso e sinal de coragem.",
    "Seus sentimentos sao validos. Voce nao esta sozinho.",
    "Respire fundo. Este momento vai passar.",
    "Pequenos passos ainda sao passos. Continue.",
    "Voce ja superou 100% dos seus piores dias.",
    "Seja gentil consigo mesmo. Voce esta fazendo o seu melhor.",
    "A tempestade nao dura para sempre. O sol vai voltar.",
    "Sua saude mental importa. Cuide de voce.",
    "Hoje e um novo dia. Uma nova chance de recomecar."
]

EXERCICIOS_RESPIRACAO = [
    {
        "nome": "Respiracao 4-7-8",
        "descricao": "Inspire por 4 segundos, segure por 7, expire por 8. Repita 4 vezes."
    },
    {
        "nome": "Respiracao Quadrada",
        "descricao": "Inspire 4s, segure 4s, expire 4s, segure 4s. Repita 5 vezes."
    },
    {
        "nome": "Respiracao Abdominal",
        "descricao": "Coloque a mao na barriga. Inspire enchendo a barriga, expire esvaziando. 10 repeticoes."
    }
]

RECURSOS_APOIO = [
    {
        "nome": "CVV - Centro de Valorizacao da Vida",
        "contato": "188 (24 horas)",
        "descricao": "Apoio emocional e prevencao do suicidio"
    },
    {
        "nome": "CAPS - Centro de Atencao Psicossocial",
        "contato": "Procure a unidade mais proxima",
        "descricao": "Atendimento gratuito em saude mental pelo SUS"
    },
    {
        "nome": "UBS - Unidade Basica de Saude",
        "contato": "Procure a unidade do seu bairro",
        "descricao": "Porta de entrada para atendimento em saude mental"
    }
]

PLAYLISTS = [
    {
        "nome": "Musicas para Relaxar",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u"
    },
    {
        "nome": "Sons da Natureza",
        "url": "https://open.spotify.com/playlist/37i9dQZF1DX4PP3DA4J0N8"
    }
]

VIDEOS_MEDITACAO = [
    {
        "nome": "Meditacao Guiada 10 min",
        "url": "https://www.youtube.com/watch?v=inpok4MKVLM"
    },
    {
        "nome": "Meditacao para Ansiedade",
        "url": "https://www.youtube.com/watch?v=O-6f5wQXSu8"
    }
]


def show_apoio_emocional():
    """Exibe secao de apoio emocional na sidebar"""
    with st.sidebar:
        with st.expander("💚 Apoio Emocional", expanded=False):
            st.caption("⚠️ *Nao substitui acompanhamento profissional*")

            # Frase motivacional
            if 'frase_idx' not in st.session_state:
                st.session_state.frase_idx = random.randint(0, len(FRASES_MOTIVACIONAIS) - 1)

            st.markdown(f"💬 *\"{FRASES_MOTIVACIONAIS[st.session_state.frase_idx]}\"*")

            if st.button("🔄 Nova frase", key="nova_frase", use_container_width=True):
                st.session_state.frase_idx = random.randint(0, len(FRASES_MOTIVACIONAIS) - 1)
                st.rerun()

            st.divider()

            # Exercicios de respiracao
            st.markdown("**🧘 Exercicios de Respiracao**")
            exercicio = random.choice(EXERCICIOS_RESPIRACAO)
            st.markdown(f"**{exercicio['nome']}**")
            st.caption(exercicio['descricao'])

            st.divider()

            # Playlists
            st.markdown("**🎵 Musicas Relaxantes**")
            for playlist in PLAYLISTS:
                st.markdown(f"[{playlist['nome']}]({playlist['url']})")

            st.divider()

            # Videos
            st.markdown("**📹 Meditacao Guiada**")
            for video in VIDEOS_MEDITACAO:
                st.markdown(f"[{video['nome']}]({video['url']})")

            st.divider()

            # Contatos de apoio
            st.markdown("**📞 Precisa de Ajuda?**")
            for recurso in RECURSOS_APOIO:
                st.markdown(f"**{recurso['nome']}**")
                st.caption(f"{recurso['contato']} - {recurso['descricao']}")

            st.warning("**Em crise? Ligue 188 (CVV) - 24 horas**")


def show_apoio_emocional_inline():
    """Exibe secao de apoio emocional inline (no resultado da traducao)"""
    st.markdown("---")
    st.markdown("### 💚 Apoio Emocional")
    st.caption("⚠️ *Este conteudo nao substitui acompanhamento profissional*")

    # Frase motivacional
    frase = random.choice(FRASES_MOTIVACIONAIS)
    st.info(f"💬 *\"{frase}\"*")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🧘 Exercicio de Respiracao**")
        exercicio = random.choice(EXERCICIOS_RESPIRACAO)
        st.markdown(f"**{exercicio['nome']}**")
        st.caption(exercicio['descricao'])

        st.markdown("**🎵 Musicas Relaxantes**")
        for playlist in PLAYLISTS:
            st.markdown(f"- [{playlist['nome']}]({playlist['url']})")

    with col2:
        st.markdown("**📹 Meditacao Guiada**")
        for video in VIDEOS_MEDITACAO:
            st.markdown(f"- [{video['nome']}]({video['url']})")

        st.markdown("**📞 Precisa de Ajuda?**")
        for recurso in RECURSOS_APOIO:
            st.caption(f"**{recurso['nome']}**: {recurso['contato']}")

    st.warning("**Em crise? Ligue 188 (CVV) - Atendimento 24 horas, gratuito**")
