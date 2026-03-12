FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files primeiro para cache
COPY package*.json ./
RUN npm ci

# Copiar código da aplicação
COPY . .

# Build para produção
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Imagem de produção
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

RUN npm install -g serve

# Expor porta (Railway usa $PORT)
EXPOSE 3000

# Servir arquivos estáticos
CMD serve -s dist -l ${PORT:-3000}
