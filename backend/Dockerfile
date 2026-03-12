FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (Railway usa $PORT)
EXPOSE 8000

# Comando padrão (Railway sobrescreve via railway.toml)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
