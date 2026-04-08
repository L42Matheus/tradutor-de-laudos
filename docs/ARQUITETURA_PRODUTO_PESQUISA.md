# Arquitetura do Sistema - Traduz Saúde

Este documento descreve a arquitetura técnica, o fluxo de dados e o modelo de persistência do projeto **Traduz Saúde**.

---

## 🏗️ Visão Geral

O sistema é dividido em uma arquitetura cliente-servidor moderna:

1.  **Frontend (SPA):** Aplicação React que lida com a interface do usuário, captura de documentos (texto/imagem/PDF) e exibição de resultados.
2.  **Backend (API):** Servidor FastAPI que processa as requisições, gerencia a autenticação, executa a lógica de anonimização e integra com a API de IA do Claude.
3.  **Banco de Dados:** SQLite para armazenamento persistente de usuários, histórico de traduções e dados epidemiológicos anonimizados.

---

## 🎨 Frontend (React)

Localizado em `/frontend`, utiliza:
- **React Query:** Para sincronização de estado com o servidor e cache de requisições.
- **Context API:** Para gerenciamento de autenticação (`AuthContext`) e preferências globais.
- **Componentes Modulares:** Divididos por domínio (especialista, suporte, tradução, UI).

---

## ⚙️ Backend (FastAPI)

Localizado em `/backend`, organizado em:
- **Routes (`app/api/routes`):** Endpoints REST divididos por funcionalidade (auth, translate, history, support, etc).
- **Services (`app/services`):** Lógica desacoplada das rotas:
    - `translator.py`: Orquestra a tradução com a IA.
    - `anonymizer.py` / `lgpd_service.py`: Garante a privacidade dos dados.
    - `file_processor.py`: Extração de conteúdo de diferentes formatos.
- **Models (`app/models`):** Definições de Schemas (Pydantic) para validação e Modelos de Banco (SQLAlchemy).

---

## 📊 Modelo de Dados (Entidades)

O banco de dados SQLite contém as seguintes tabelas principais:

### **Usuários e Sessões**
- `users`: Armazena dados de pacientes, especialistas e administradores.
- `user_consents`: Registro histórico de aceites de termos e consentimento para pesquisa.
- `auth_sessions`: Controle de sessões via tokens.

### **Tradução e Histórico**
- `traducoes`: Registro principal de cada processamento realizado (original, traduzido, glossário).
- `translation_history`: Vínculo entre traduções e usuários autenticados para exibição no perfil.

### **Especialista e Revisão**
- `revisoes_especialista`: Notas (fidelidade, clareza, risco) e comentários deixados por médicos sobre traduções da IA.
- Fila de Revisão: Gerenciada via status na tabela de traduções.

### **Epidemiologia**
- `epidemio_metadados`: Dados sanitizados (município, estado, categoria da doença, faixa etária) para dashboards de saúde pública, sem qualquer vínculo com a identidade do paciente (Compliance LGPD).

---

## 🔒 Fluxo de Privacidade (LGPD)

O Traduz Saúde foi desenhado com o conceito de *Privacy by Design*:

1.  **Captura:** O documento é recebido pelo backend.
2.  **Sanitização:** O `anonymizer.py` identifica e remove nomes, documentos, telefones e endereços específicos.
3.  **Processamento:** Apenas o conteúdo clínico anonimizado é enviado para a API da Anthropic.
4.  **Armazenamento:**
    - O histórico pessoal é criptografado/protegido por autenticação.
    - Os dados para pesquisa são movidos para a tabela de metadados epidemiológicos sem chaves estrangeiras que permitam a reidentificação (anonymized data).

---

## 📡 Fluxo de Tradução

1.  **Frontend** → Envia arquivo/texto para `/api/v1/translate`.
2.  **Backend** → Extrai texto → Anonimiza → Seleciona Prompt especializado.
3.  **Claude API** → Retorna JSON estruturado (Resumo, Detalhes, Glossário).
4.  **Backend** → Salva no DB → Retorna para o Frontend.
5.  **Frontend** → Exibe resultados em abas formatadas.
