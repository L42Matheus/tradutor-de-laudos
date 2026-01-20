# Tradutor de Laudos Medicos

Sistema para traduzir laudos medicos em linguagem tecnica para linguagem acessivel ao paciente.

## O que faz?

- Traduz laudos medicos para linguagem simples
- Aceita upload de arquivos (PDF, imagens) ou texto colado
- Le imagens de laudos usando visao computacional (Claude Vision)
- Remove automaticamente dados pessoais (LGPD)
- Explica termos tecnicos
- Nao armazena nenhum dado
- Interface web facil de usar

## IMPORTANTE

**Este sistema NAO substitui consulta medica!**
E apenas uma ferramenta educacional para ajudar pacientes a entenderem melhor seus exames.

---

## Como Instalar e Rodar

### 1. Pre-requisitos
- Python 3.8 ou superior
- Conta na Anthropic (para API do Claude)

### 2. Pegue sua API Key
1. Acesse: https://console.anthropic.com/
2. Faca login ou crie uma conta
3. Va em "API Keys"
4. Crie uma nova chave
5. Copie a chave (comeca com `sk-ant-...`)

### 3. Instalacao

```bash
git clone https://github.com/L42Matheus/tradutor-de-laudos.git
cd tradutor-de-laudos

python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configuracao

```bash
cp .env.example .env
# Edite o .env e adicione sua API key
```

### 5. Rodar

```bash
streamlit run app.py
```

---

## Como Usar

1. Aceite os termos de uso
2. Selecione o tipo de exame
3. Escolha como enviar o laudo:
   - Upload de arquivo (PDF, imagem, TXT)
   - Colar texto diretamente
4. Clique em "Traduzir Laudo"
5. Veja o resultado em 3 niveis:
   - Resumo simples
   - Explicacao detalhada
   - Glossario de termos

---

## Estrutura do Projeto

```
tradutor-laudos/
├── app.py              # Interface Streamlit
├── translator.py       # Logica de traducao com Claude
├── file_reader.py      # Processamento de arquivos
├── anonymizer.py       # Remove dados pessoais
├── prompts.py          # Prompts por tipo de exame
├── requirements.txt    # Dependencias
├── .env.example        # Template de configuracao
└── docs/               # Documentacao adicional
    ├── TECNOLOGIAS.md
    ├── MELHORIAS.md
    └── FEATURES.md
```

---

## Documentacao

- [Tecnologias Utilizadas](docs/TECNOLOGIAS.md)
- [Melhorias de Layout](docs/MELHORIAS.md)
- [Novas Features Planejadas](docs/FEATURES.md)

---

## Licenca

MIT License
