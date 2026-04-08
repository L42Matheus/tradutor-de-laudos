# Arquitetura Postgres e RAG

## Objetivo

Preparar o Traduz Saúde para:

- persistência transacional em `Postgres`
- `pgvector` para a primeira versão do RAG
- storage externo por referência, sem depender de base64 no banco canônico
- separação clara entre ingestão, clínica, produto e analytics

## Camadas

### Ingestão

- upload de PDF, texto e imagem
- OCR/parser
- versionamento do documento
- armazenamento do arquivo original por referência

Tabelas principais:

- `documents`
- `document_assets`
- `document_versions`

### Clínica

- tradução em linguagem acessível
- alertas do modelo
- alertas determinísticos por regra
- base para RAG com fontes oficiais

Tabelas principais:

- `translations`
- `clinical_alerts`
- `rag_sources`
- `rag_chunks`

### Produto

- autenticação
- consentimento
- histórico
- revisão por especialista

Tabelas principais:

- `users`
- `user_consents`
- `auth_sessions`
- `translation_reviews`

### Analytics

- eventos anonimizados
- base para mapa epidemiológico
- agregação por município, estado, faixa etária e categoria clínica

Tabela principal:

- `epidemiology_events`

## Pipeline alvo

1. upload
2. OCR/parser
3. classificação do documento
4. extração de entidades clínicas básicas
5. retrieval em fontes SUS/TUSS/PCDT/CONITEC/protocolos
6. geração ancorada
7. regras determinísticas de risco
8. resposta final para paciente
9. persistência com versão de pipeline

## Fase 1 implementada nesta branch

- `DATABASE_URL` no backend
- `docker-compose` com `Postgres + pgvector`
- `Alembic` para migração inicial
- schema novo em paralelo ao legado
- persistência canônica em:
  - `documents`
  - `document_assets`
  - `document_versions`
  - `translations`
  - `clinical_alerts`
  - `translation_reviews`
  - `epidemiology_events`
  - `rag_sources`
  - `rag_chunks`
- storage local por referência em `backend/storage`
- sincronização inicial dos fluxos de:
  - tradução padrão
  - processamento epidemiológico
  - revisão de especialista

## Compatibilidade

Para não quebrar o produto já em uso:

- `translation_history`
- `traducoes`
- `epidemio_metadados`
- `revisoes_especialista`

continuam existindo nesta fase como camada de compatibilidade.

O próximo passo recomendado é migrar leitura de histórico e revisão totalmente para `translations` e `translation_reviews`, reduzindo a sobreposição residual.
