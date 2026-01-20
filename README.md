# 🏥 Tradutor de Laudos Médicos - MVP

Sistema simples para traduzir laudos médicos em linguagem técnica para linguagem acessível ao paciente.

## 🎯 O que faz?

- ✅ Traduz laudos médicos para linguagem simples
- ✅ Remove automaticamente dados pessoais (LGPD)
- ✅ Explica termos técnicos
- ✅ Não armazena nenhum dado
- ✅ Interface web fácil de usar

## ⚠️ IMPORTANTE

**Este sistema NÃO substitui consulta médica!**  
É apenas uma ferramenta educacional para ajudar pacientes a entenderem melhor seus exames.

---

## 🚀 Como instalar e rodar

### 1. **Pré-requisitos**
- Python 3.8 ou superior
- Conta na Anthropic (para API do Claude)

### 2. **Pegue sua API Key**
1. Acesse: https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Vá em "API Keys"
4. Crie uma nova chave
5. Copie a chave (começa com `sk-ant-...`)

### 3. **Instalação**

```bash
# Clone ou baixe este projeto
cd tradutor-laudos

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Mac/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 4. **Configuração**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione sua API key
# No Windows: notepad .env
# No Mac/Linux: nano .env
```

Cole sua API key no lugar de `sk-ant-sua-chave-aqui`

### 5. **Rodar o sistema**

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

---

## 📖 Como usar

1. **Aceite os termos** de uso
2. **Selecione o tipo de exame**
3. **Cole o texto do laudo** na área de texto
4. **Clique em "Traduzir Laudo"**
5. **Veja o resultado** em 3 níveis:
   - Resumo simples
   - Explicação detalhada
   - Glossário de termos

---

## 🔒 Privacidade e Segurança

### Dados Removidos Automaticamente:
- ✅ CPF
- ✅ RG
- ✅ Nomes
- ✅ Telefones
- ✅ Emails
- ✅ Endereços
- ✅ Datas de nascimento

### Como funciona:
1. Você cola o laudo
2. Sistema remove dados pessoais
3. Envia para API apenas texto médico
4. Nada é armazenado
5. Dados descartados após uso

---

## 💰 Custos

### API do Claude:
- **Modelo usado**: Claude Sonnet 4
- **Custo médio**: ~$0.003 por laudo (menos de 1 centavo)
- **Com $5 de crédito**: ~1.600 laudos

### Onde adicionar créditos:
https://console.anthropic.com/settings/billing

---

## 🛠️ Estrutura do Projeto

```
tradutor-laudos/
│
├── app.py              # Interface Streamlit
├── translator.py       # Lógica de tradução com Claude
├── anonymizer.py       # Remove dados pessoais
├── prompts.py          # Prompts otimizados por tipo
├── requirements.txt    # Dependências
├── .env.example        # Template de configuração
└── README.md          # Este arquivo
```

---

## 🚀 Próximos Passos (Validação)

### Para testar com usuários reais:

1. **Validação com amigos/família**
   - Peça laudos antigos (anonimize manualmente se necessário)
   - Teste diferentes tipos de exames
   - Colete feedback sobre clareza

2. **Feedback de médicos**
   - Mostre as traduções para médicos conhecidos
   - Pergunte se as explicações estão corretas
   - Ajuste prompts baseado no feedback

3. **Métricas a observar**
   - Paciente entendeu melhor o exame?
   - Gerou dúvidas novas?
   - Ficou mais ou menos ansioso?
   - Conseguiu fazer perguntas melhores ao médico?

---

## 📋 Deploy (Futuro)

### Opções gratuitas:
- **Streamlit Cloud**: Deploy gratuito direto do GitHub
- **Render**: Plano gratuito com Python
- **Railway**: Horas gratuitas por mês

### Para escalar:
- Considere cache de respostas comuns
- Monitore custos da API
- Implemente rate limiting

---

## ⚖️ Aspectos Legais

### LGPD:
✅ Não armazena dados  
✅ Anonimização automática  
✅ Termo de consentimento  
✅ Processamento temporário  

### Responsabilidade:
- Sistema é educacional
- Não faz diagnósticos
- Não substitui médico
- Usuário assume responsabilidade pelo uso

---

## 🤝 Contribuindo

Sugestões de melhoria:
1. Fork o projeto
2. Crie uma branch (`git checkout -b melhoria-xyz`)
3. Commit suas mudanças (`git commit -am 'Adiciona xyz'`)
4. Push para a branch (`git push origin melhoria-xyz`)
5. Abra um Pull Request

---

## 📞 Suporte

Problemas? Dúvidas?
1. Verifique se a API key está correta
2. Confirme que tem créditos na conta Anthropic
3. Teste com um laudo simples primeiro
4. Cheque os logs de erro no terminal

---

## 📄 Licença

MIT License - use livremente, mas sem garantias.

---

## ✨ Créditos

Desenvolvido com:
- Streamlit (interface)
- Claude API (tradução)
- Python (backend)

**Feito para ajudar pessoas a entenderem melhor sua saúde! 🏥❤️**
