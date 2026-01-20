# Tecnologias Utilizadas

## Python 3.13

**Por que Python?**
- Linguagem versatil com excelente suporte para processamento de texto
- Grande ecossistema de bibliotecas para IA e machine learning
- Integracao nativa com APIs REST
- Comunidade ativa e documentacao abundante
- Facil de aprender e manter

---

## Streamlit

**O que e?**
Framework Python para criar interfaces web interativas rapidamente.

**Por que Streamlit?**
- Nao requer conhecimento de frontend (HTML/CSS/JavaScript)
- Prototipagem rapida - menos codigo, mais resultado
- Deploy simples e gratuito via Streamlit Cloud
- Componentes prontos para upload de arquivos, formularios, graficos
- Hot reload - alteracoes aparecem instantaneamente
- Ideal para MVPs e validacao de ideias

**Alternativas consideradas:**
- Flask/Django: Requerem mais codigo e conhecimento de frontend
- Gradio: Similar, mas menos flexivel para customizacao
- React/Vue: Curva de aprendizado maior, mais complexo

---

## Claude API (Anthropic)

**O que e?**
API de inteligencia artificial da Anthropic para processamento de linguagem natural.

**Por que Claude?**
- Excelente compreensao de textos medicos complexos
- Geracao de explicacoes claras e acessiveis
- Suporte nativo a visao computacional (le imagens de laudos)
- Contexto grande (200k tokens) - processa laudos extensos
- Respostas estruturadas em JSON
- Menos "alucinacoes" que concorrentes em textos tecnicos

**Modelo utilizado:** Claude Sonnet 4
- Equilibrio entre qualidade e velocidade
- Otimo para tarefas que requerem precisao

**Alternativas consideradas:**
- GPT-4 (OpenAI): Similar em qualidade, mas mais caro
- Gemini (Google): Bom, mas API menos madura
- Modelos locais (Llama, Mistral): Requerem GPU, mais complexo

---

## PyPDF2

**O que e?**
Biblioteca Python para leitura e manipulacao de arquivos PDF.

**Por que PyPDF2?**
- Leve e sem dependencias externas complexas
- Extrai texto de PDFs nativos (nao escaneados)
- Facil integracao com o resto do projeto
- Codigo aberto e bem mantido

**Limitacoes:**
- Nao faz OCR (PDFs escaneados nao funcionam)
- Para OCR, seria necessario adicionar Tesseract ou usar Claude Vision

---

## Pillow

**O que e?**
Biblioteca padrao para processamento de imagens em Python.

**Por que Pillow?**
- Necessaria para manipular imagens antes de enviar para API
- Suporta todos os formatos comuns (JPEG, PNG, GIF, WebP)
- Leve e eficiente
- Padrao da industria para imagens em Python

---

## python-dotenv

**O que e?**
Biblioteca para carregar variaveis de ambiente de arquivos .env.

**Por que python-dotenv?**
- Mantem API keys fora do codigo fonte
- Seguranca: .env fica no .gitignore
- Facilita deploy em diferentes ambientes
- Padrao da industria para configuracao

---

## Arquitetura Geral

```
Usuario
   │
   ▼
┌─────────────────┐
│   Streamlit     │  ← Interface web
│    (app.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  file_reader.py │  ← Processa PDF/Imagem/Texto
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  anonymizer.py  │  ← Remove dados pessoais
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  translator.py  │  ← Envia para Claude API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Claude API    │  ← Processa e retorna traducao
└─────────────────┘
```

---

## Decisoes Tecnicas

### Por que nao usar banco de dados?
- Privacidade: nao armazenamos laudos
- Simplicidade: menos infraestrutura
- LGPD: menos responsabilidade legal
- Performance: menos latencia

### Por que processar tudo em memoria?
- Seguranca: dados nao persistem
- Velocidade: sem I/O de disco
- Escalabilidade: stateless, facil de escalar

### Por que Claude ao inves de modelo local?
- Qualidade superior para textos medicos
- Sem necessidade de GPU
- Atualizacoes automaticas do modelo
- Suporte a visao sem configuracao adicional
