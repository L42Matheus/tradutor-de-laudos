# Tecnologias Utilizadas

Este documento detalha as escolhas tecnológicas para o projeto **Traduz Saúde**, justificando o uso de cada ferramenta na arquitetura atual de frontend e backend.

---

## 🎨 Frontend

O frontend foi reconstruído para oferecer uma experiência de usuário (UX) fluida, responsiva e tipada.

### **React + TypeScript**
- **Por que?** Garante segurança de tipos, componentes reutilizáveis e uma vasta biblioteca de ecossistema.
- **Vite:** Utilizado como build tool para carregamento instantâneo (HMR) e builds otimizados.

### **Tailwind CSS**
- **Por que?** Permite estilização rápida e responsiva diretamente no HTML, mantendo o design consistente sem escrever CSS customizado verboso.

### **TanStack Query (React Query)**
- **Por que?** Gerencia o estado das requisições à API, lidando automaticamente com cache, estados de loading e erros.

### **Axios**
- **Por que?** Cliente HTTP robusto para comunicação com o backend FastAPI.

### **Lucide React**
- **Por que?** Biblioteca de ícones leve e moderna que se integra perfeitamente com React.

---

## ⚙️ Backend (API)

O backend é uma API robusta construída para ser rápida, segura e escalável.

### **FastAPI (Python 3.10+)**
- **Por que?** Extremamente rápido (comparável a Node.js e Go), com documentação automática (Swagger/OpenAPI) e suporte nativo a operações assíncronas.

### **SQLAlchemy + SQLite**
- **Por que?** O SQLAlchemy é o ORM padrão da indústria para Python, facilitando a manipulação de dados. O SQLite foi escolhido pela simplicidade de configuração inicial (sem necessidade de servidor de DB separado), ideal para MVPs e protótipos locais.

### **Pydantic v2**
- **Por que?** Utilizado para validação de dados e definição de schemas, garantindo que a entrada e saída da API estejam sempre corretas.

---

## 🧠 Inteligência Artificial

### **Claude 3.5 Sonnet (Anthropic API)**
- **Por que?** 
  - **Precisão Médica:** Demonstra excelente capacidade de interpretar termos técnicos complexos sem alucinar.
  - **Visão Computacional:** Processa imagens de laudos diretamente, identificando textos manuscritos ou impressos com alta fidelidade.
  - **Contexto Amplo:** Lida bem com documentos longos e gera respostas estruturadas em JSON.

---

## 📄 Processamento de Arquivos

### **PyPDF2**
- **O que faz?** Extrai texto de arquivos PDF digitais (não escaneados).

### **Pillow (PIL)**
- **O que faz?** Manipula e otimiza imagens antes de serem enviadas para a API do Claude para análise visual.

---

## 🔒 Segurança e Privacidade

### **Anonymizer (Lógica Customizada)**
- O sistema utiliza algoritmos de detecção de PII (Personally Identifiable Information) para remover nomes, CPFs, datas de nascimento e contatos antes de enviar qualquer dado para a nuvem da Anthropic, garantindo conformidade com a **LGPD**.

### **python-dotenv**
- Mantém chaves de API e segredos do banco de dados fora do código-fonte, utilizando variáveis de ambiente seguras.

---

## 🚀 Infraestrutura (Provisionada para)

- **Docker:** O projeto inclui Dockerfiles para frontend e backend, facilitando o deploy em qualquer nuvem.
- **Railway/Vercel:** Configurações prontas para deploy rápido nessas plataformas.
