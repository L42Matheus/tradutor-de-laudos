# Traduz Saúde

Sistema inteligente para traduzir laudos e receitas médicas de linguagem técnica complexa para uma linguagem acessível e compreensível ao paciente.

## 🚀 O que faz?

- **Tradução Inteligente:** Converte termos médicos difíceis em explicações simples usando IA (Claude 3.5 Sonnet).
- **Múltiplos Níveis:** Gera um resumo simplificado, uma explicação detalhada e um glossário de termos.
- **Privacidade e LGPD:** Remove automaticamente dados pessoais (PII) antes do processamento.
- **Suporte a Arquivos:** Aceita texto colado, PDFs e imagens de laudos/receitas.
- **Visão Computacional:** Lê imagens de documentos médicos diretamente.
- **Apoio Emocional:** Identifica diagnósticos sensíveis e oferece suporte e orientações.
- **Área de Especialista:** Permite que profissionais de saúde revisem e validem as traduções.

## ⚠️ IMPORTANTE

**Este sistema NÃO substitui consulta médica!**
É apenas uma ferramenta informativa para ajudar pacientes a entenderem melhor seus exames e prepararem perguntas para seus médicos. Nunca altere tratamentos ou tome decisões clínicas baseadas apenas nesta tradução.

---

## 🛠️ Arquitetura

O projeto agora utiliza uma arquitetura moderna separada em Frontend e Backend:

- **Frontend:** React + TypeScript + Vite + Tailwind CSS.
- **Backend:** FastAPI (Python) + Postgres + Alembic + pgvector + Anthropic (Claude API).
- **Storage:** filesystem local na fase 1, com referência em banco para evoluir depois para S3/R2.

---

## ⚙️ Como Instalar e Rodar

### 1. Pré-requisitos
- **Python 3.10** ou superior.
- **Node.js 18** ou superior (para o frontend).
- **Chave de API da Anthropic** (Claude).

### 2. Configuração do Backend

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edite o .env e adicione sua ANTHROPIC_API_KEY
```

Para subir a stack com Postgres local:
```bash
docker compose up -d postgres backend
```

Para rodar o backend:
```bash
python run.py
# O servidor iniciará em http://localhost:8000
# Documentação da API disponível em http://localhost:8000/docs
```

### 3. Configuração do Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Verifique se a VITE_API_URL aponta para o seu backend
```

Para rodar o frontend:
```bash
npm run dev
# Acesse em http://localhost:5173
```

---

## 📂 Estrutura do Projeto

```
tradutor-de-laudos/
├── backend/            # API em FastAPI
│   ├── app/            # Código fonte do backend
│   │   ├── api/        # Endpoints (auth, translate, history, etc)
│   │   ├── models/     # Modelos de dados e schemas
│   │   ├── services/   # Lógica de negócio (translator, anonymizer)
│   │   └── prompts/    # Prompts especializados para a IA
│   └── tests/          # Testes automatizados do backend
├── frontend/           # Interface em React
│   ├── src/            # Código fonte do frontend
│   │   ├── components/ # Componentes UI reaproveitáveis
│   │   ├── pages/      # Páginas (Home, Auth, Especialista)
│   │   └── services/   # Integração com a API
│   └── public/         # Assets estáticos
├── docs/               # Documentação detalhada
└── app.py              # (Legado) Interface original em Streamlit
```

---

## 📖 Documentação Adicional

- [Tecnologias Utilizadas](docs/TECNOLOGIAS.md)
- [Arquitetura e Produto](docs/ARQUITETURA_PRODUTO_PESQUISA.md)
- [Arquitetura Postgres e RAG](docs/ARQUITETURA_POSTGRES_RAG.md)
- [Roadmap de Features](docs/FEATURES.md)
- [Melhorias de Layout](docs/MELHORIAS.md)

---

## ⚖️ Licença

MIT License
