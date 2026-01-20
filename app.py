import streamlit as st
import os
from dotenv import load_dotenv
from translator import LaudoTranslator
from anonymizer import anonymize_text
from file_reader import process_uploaded_file

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Tradutor de Laudos Médicos",
    page_icon="🏥",
    layout="wide"
)

# Título e descrição
st.title("🏥 Tradutor de Laudos Médicos")
st.markdown("*Entenda seus exames de forma simples e clara*")

# Termo de consentimento
with st.expander("⚠️ IMPORTANTE: Leia antes de usar", expanded=False):
    st.markdown("""
    ### Termos de Uso e Privacidade

    ✅ **Seus dados estão seguros:**
    - Não armazenamos nenhum laudo ou informação pessoal
    - Dados pessoais são automaticamente removidos antes do processamento
    - Tudo é processado em memória e descartado após a tradução

    ⚠️ **Este serviço NÃO substitui consulta médica:**
    - Use apenas para melhor compreensão dos seus exames
    - Sempre consulte seu médico para interpretação oficial
    - Em caso de dúvidas, procure um profissional de saúde

    📋 **LGPD:**
    - Seus dados são processados de forma anônima
    - Não compartilhamos informações com terceiros
    - Você pode usar o serviço sem fornecer dados pessoais
    """)

consent = st.checkbox("Li e concordo com os termos acima")

if consent:
    # Verificar API Key
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        st.error("⚠️ Configuração necessária: adicione sua ANTHROPIC_API_KEY no arquivo .env")
        st.info("Veja o arquivo .env.example para instruções")
        st.stop()

    # Inicializar tradutor
    translator = LaudoTranslator(api_key)

    # Seletor de tipo de exame
    tipo_exame = st.selectbox(
        "Tipo de exame:",
        ["Exame de Sangue", "Exame de Imagem (RX, TC, RM)", "Exame de Urina", "Biópsia/Patologia", "Outro"]
    )

    # Upload de arquivo
    st.subheader("📁 Envie seu laudo")
    st.markdown("Formatos aceitos: **PDF**, **Imagem** (JPG, PNG) ou **Texto** (TXT)")

    uploaded_file = st.file_uploader(
        "Escolha o arquivo do laudo",
        type=['pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'webp'],
        help="Envie o arquivo do seu laudo médico. Aceitamos PDF, imagens e arquivos de texto."
    )

    # Mostrar preview do arquivo
    if uploaded_file:
        file_details = f"**Arquivo:** {uploaded_file.name} | **Tamanho:** {uploaded_file.size / 1024:.1f} KB"
        st.caption(file_details)

        # Preview para imagens
        if uploaded_file.type.startswith('image/'):
            st.image(uploaded_file, caption="Preview do laudo", use_container_width=True)
            uploaded_file.seek(0)  # Reset para leitura posterior

    # Botão de tradução
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        traduzir_btn = st.button("🔄 Traduzir Laudo", use_container_width=True, type="primary")

    if traduzir_btn and uploaded_file:
        with st.spinner("Analisando seu laudo... ⏳"):
            try:
                # Processar arquivo
                file_data = process_uploaded_file(uploaded_file)

                if file_data['error']:
                    st.error(f"❌ {file_data['error']}")
                    st.stop()

                # Processar baseado no tipo de arquivo
                if file_data['type'] == 'text':
                    # Anonimizar o texto
                    laudo_anonimizado, dados_removidos = anonymize_text(file_data['content'])

                    if dados_removidos:
                        st.info(f"🔒 Dados pessoais removidos para sua segurança: {', '.join(dados_removidos)}")

                    # Traduzir o laudo
                    resultado = translator.translate(laudo_anonimizado, tipo_exame)

                elif file_data['type'] == 'image':
                    st.info("🖼️ Processando imagem do laudo...")
                    # Traduzir imagem diretamente (Claude Vision)
                    resultado = translator.translate_image(
                        file_data['content'],
                        file_data['media_type'],
                        tipo_exame
                    )

                else:
                    st.error("❌ Tipo de arquivo não reconhecido")
                    st.stop()

                # Exibir resultado
                st.success("✅ Tradução concluída!")

                # Tabs para diferentes níveis de explicação
                tab1, tab2, tab3 = st.tabs(["📋 Resumo Simples", "🔍 Explicação Detalhada", "📚 Termos Técnicos"])

                with tab1:
                    st.markdown("### Resumo em Linguagem Simples")
                    st.markdown(resultado.get('resumo', 'Não disponível'))

                with tab2:
                    st.markdown("### Explicação Detalhada")
                    st.markdown(resultado.get('detalhado', 'Não disponível'))

                with tab3:
                    st.markdown("### Glossário de Termos Técnicos")
                    st.markdown(resultado.get('glossario', 'Não disponível'))

                # Avisos importantes
                if resultado.get('alertas'):
                    st.warning("⚠️ " + resultado['alertas'])

                st.info("💡 **Lembre-se:** Esta tradução é apenas informativa. Sempre consulte seu médico!")

            except Exception as e:
                st.error(f"❌ Erro ao processar o laudo: {str(e)}")
                st.info("Tente novamente ou entre em contato com o suporte.")

    elif traduzir_btn and not uploaded_file:
        st.warning("⚠️ Por favor, envie um arquivo de laudo antes de traduzir.")

else:
    st.warning("⚠️ Por favor, leia e aceite os termos de uso para continuar.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🏥 Tradutor de Laudos Médicos | Desenvolvido para facilitar o entendimento de exames</p>
    <p style='font-size: 0.8em;'>Este serviço não substitui consulta médica profissional</p>
</div>
""", unsafe_allow_html=True)
