"""
Estilos CSS customizados para o Traduz Saude
"""


def get_custom_css(theme: str = "dark") -> str:
    """Retorna CSS customizado baseado no tema"""

    # Cores baseadas no tema
    if theme == "light":
        # Tema claro - Azul Bebê Clean
        bg_color = "#f0f8ff"
        text_color = "#2c3e50"
        card_bg = "#ffffff"
        border_color = "#b8d4e8"
        accent_color = "#4a90b8"
        secondary_text = "#5a6c7d"
        header_bg = "linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%)"
        input_bg = "#ffffff"
        label_color = "#2c3e50"
        button_bg = "linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%)"
    else:
        # Tema escuro
        bg_color = "#0e1117"
        text_color = "#fafafa"
        card_bg = "#1e1e2e"
        border_color = "#333344"
        accent_color = "#00d4ff"
        secondary_text = "#b0b0b0"
        header_bg = "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
        input_bg = "#1e1e2e"
        label_color = "#fafafa"
        button_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    return f"""
    <style>
        /* === RESET E BASE === */
        .stApp {{
            background-color: {bg_color};
        }}

        /* === TEXTOS E LABELS === */
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div {{
            color: {text_color};
        }}

        .stMarkdown, .stMarkdown p {{
            color: {text_color} !important;
        }}

        /* Labels dos inputs */
        .stSelectbox label, .stRadio label, .stCheckbox label,
        .stTextArea label, .stFileUploader label {{
            color: {label_color} !important;
        }}

        /* Subheaders */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
            color: {text_color} !important;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {card_bg};
        }}

        [data-testid="stSidebar"] * {{
            color: {text_color};
        }}

        /* === HEADER / TITULO === */
        .main-header {{
            background: {header_bg};
            padding: 2rem 1rem;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
            text-align: center;
        }}

        .main-header h1 {{
            color: white !important;
            font-size: clamp(1.8rem, 5vw, 3rem);
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .main-header p {{
            color: rgba(255,255,255,0.9);
            font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            margin: 0.5rem 0 0 0;
        }}

        /* === TOGGLE DE TEMA === */
        .theme-toggle {{
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 1000;
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 50px;
            padding: 8px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            color: {text_color};
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .theme-toggle:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}

        /* === CARDS E CONTAINERS === */
        .stExpander {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
        }}

        /* === RESPONSIVIDADE MOBILE === */
        @media (max-width: 768px) {{
            .main-header {{
                padding: 1.5rem 0.5rem;
                margin: -1rem -0.5rem 1.5rem -0.5rem;
                border-radius: 0 0 15px 15px;
            }}

            .stRadio > div {{
                flex-direction: column !important;
                gap: 0.5rem;
            }}

            .stRadio > div > label {{
                width: 100% !important;
                justify-content: center;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0;
                flex-wrap: wrap;
            }}

            .stTabs [data-baseweb="tab"] {{
                flex: 1;
                min-width: 100px;
                font-size: 0.85rem;
                padding: 8px 12px;
            }}

            .stButton > button {{
                width: 100% !important;
                padding: 0.75rem 1rem;
                font-size: 1rem;
            }}

            .stTextArea textarea {{
                font-size: 16px; /* Previne zoom no iOS */
            }}

            .theme-toggle {{
                top: auto;
                bottom: 20px;
                right: 20px;
                padding: 6px 12px;
                font-size: 0.8rem;
            }}

            /* Ajusta colunas para mobile */
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
            }}
        }}

        @media (max-width: 480px) {{
            .main-header h1 {{
                font-size: 1.6rem;
            }}

            .main-header p {{
                font-size: 0.85rem;
            }}

            .stTabs [data-baseweb="tab"] {{
                min-width: 80px;
                font-size: 0.75rem;
                padding: 6px 8px;
            }}
        }}

        /* === MELHORIAS GERAIS === */
        .stSelectbox, .stRadio {{
            margin-bottom: 1rem;
        }}

        .stButton > button[kind="primary"] {{
            background: {button_bg};
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            color: white !important;
        }}

        .stButton > button[kind="primary"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(116, 185, 255, 0.4);
        }}

        /* === TABS ESTILIZADAS === */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {card_bg};
            border-radius: 10px;
            padding: 5px;
            gap: 5px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            color: {secondary_text};
            transition: all 0.2s ease;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {accent_color}20;
            color: {accent_color};
        }}

        /* === FOOTER === */
        .custom-footer {{
            text-align: center;
            padding: 2rem 1rem;
            margin-top: 3rem;
            border-top: 1px solid {border_color};
            color: {secondary_text};
        }}

        .custom-footer p {{
            margin: 0.25rem 0;
        }}

        /* === FILE UPLOADER === */
        [data-testid="stFileUploader"] {{
            background-color: {card_bg} !important;
            border: 2px dashed {border_color};
            border-radius: 12px;
            padding: 1rem;
            transition: all 0.3s ease;
        }}

        [data-testid="stFileUploader"]:hover {{
            border-color: {accent_color};
            background-color: {bg_color} !important;
        }}

        [data-testid="stFileUploader"] * {{
            color: {text_color} !important;
        }}

        [data-testid="stFileUploader"] button {{
            background-color: {accent_color} !important;
            color: white !important;
            border: none !important;
        }}

        [data-testid="stFileUploader"] section {{
            background-color: {card_bg} !important;
        }}

        [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {{
            background-color: {card_bg} !important;
        }}

        /* === ALERTAS E MENSAGENS === */
        .stAlert {{
            border-radius: 10px;
        }}

        /* === CHECKBOX TERMOS === */
        .stCheckbox {{
            padding: 0.5rem;
            background: {card_bg};
            border-radius: 8px;
            border: 1px solid {border_color};
        }}

        .stCheckbox label span {{
            color: {text_color} !important;
        }}

        /* === INPUTS E SELECTS === */
        .stSelectbox > div > div,
        .stTextArea textarea {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border-color: {border_color} !important;
        }}

        /* Radio buttons */
        .stRadio > div {{
            background-color: transparent;
        }}

        .stRadio label span {{
            color: {text_color} !important;
        }}

        /* Expander */
        .stExpander summary {{
            color: {text_color} !important;
        }}

        .stExpander summary span {{
            color: {text_color} !important;
        }}

        /* Warning e Info boxes */
        .stAlert p {{
            color: inherit !important;
        }}

        /* Code blocks (botao copiar) */
        .stCode, [data-testid="stCode"] {{
            background-color: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}

        .stCode code, [data-testid="stCode"] code {{
            color: {text_color} !important;
            background-color: {card_bg} !important;
        }}

        .stCode pre, [data-testid="stCode"] pre {{
            color: {text_color} !important;
            background-color: {card_bg} !important;
        }}

        /* Expander do copiar tudo */
        .stExpander [data-testid="stCode"] {{
            background-color: {input_bg} !important;
        }}
    </style>
    """


def get_header_html() -> str:
    """Retorna HTML do header estilizado"""
    return """
    <div class="main-header">
        <h1>Traduz Saude</h1>
        <p>Entenda seus exames e receitas de forma simples e clara</p>
    </div>
    """


def get_footer_html() -> str:
    """Retorna HTML do footer estilizado"""
    return """
    <div class="custom-footer">
        <p>Traduz Saude</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">
            Este servico nao substitui consulta medica profissional
        </p>
    </div>
    """
