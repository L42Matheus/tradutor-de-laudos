# Roadmap do Traduz Saúde

Este documento descreve as funcionalidades atuais e o planejamento futuro para o sistema.

---

## ✅ Funcionalidades Implementadas (v1.0)

### **Tradução e IA**
- [x] Tradução de laudos e receitas para linguagem simples.
- [x] Geração de resumo, detalhes e glossário.
- [x] Processamento de texto, PDF e Imagem (Visão Computacional).
- [x] Anonimização automática de dados sensíveis (LGPD).
- [x] Identificação de categorias de exames (Cardiovascular, Oncológico, etc).

### **Interface e Experiência (UX)**
- [x] Interface moderna e responsiva com React e Tailwind.
- [x] Suporte a Tema Escuro e Claro (Dark/Light Mode).
- [x] Botão para copiar resultados para a área de transferência.
- [x] Alertas visuais para diagnósticos sensíveis.
- [x] Componentes de apoio emocional integrados.

### **Gestão e Especialistas**
- [x] Autenticação de usuários (Pacientes e Especialistas).
- [x] Fila de revisão para médicos auditarem as traduções da IA.
- [x] Painel de estatísticas básicas para especialistas.
- [x] Histórico de traduções salvo no banco de dados.

---

## 🚀 Próximos Passos (Curto Prazo)

### **Processamento de Arquivos**
- [ ] Suporte a múltiplas páginas de PDF.
- [ ] OCR avançado para PDFs de baixa qualidade (fotos de PDF).
- [ ] Suporte a documentos do Word (.docx).
- [ ] Compressão automática de imagens pesadas antes do envio.

### **Funcionalidades Médicas**
- [ ] Detecção automática do tipo de exame sem necessidade de seleção manual.
- [ ] Níveis de detalhe ajustáveis (Básico, Intermediário, Avançado).
- [ ] Sugestão de perguntas inteligentes para o paciente fazer ao médico.

---

## 🛰️ Visão de Médio e Longo Prazo

### **Ecossistema e Integrações**
- [ ] **Bot WhatsApp:** Envio de fotos de laudos diretamente pelo chat.
- [ ] **Histórico Evolutivo:** Comparação entre dois exames iguais feitos em datas diferentes para mostrar a evolução.
- [ ] **Exportação:** Gerar PDF formatado da tradução para impressão.
- [ ] **Acessibilidade:** Implementar leitor de tela e suporte a comandos de voz.

### **Inteligência e Dados**
- [ ] **Dashboard Epidemiológico:** Mapa de calor de condições de saúde por região (dados anonimizados).
- [ ] **Modelo Local:** Opção de rodar modelos menores localmente (via Ollama) para máxima privacidade.
- [ ] **Integração com Prontuários:** Importação direta de sistemas de saúde (SUS/Planos).

---

## 🛠️ Backlog Técnico
- [ ] Implementar filas de processamento assíncrono (Celery/Redis) para laudos pesados.
- [ ] Aumentar a cobertura de testes unitários no frontend.
- [ ] Implementar Rate Limiting na API para evitar abusos.
- [ ] Documentação completa da API via Swagger (OpenAPI).
