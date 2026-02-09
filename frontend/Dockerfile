FROM node:20-alpine

WORKDIR /app

# Copiar package files primeiro para cache
COPY package*.json ./
RUN npm install

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 5173

# Comando padrão para desenvolvimento
CMD ["npm", "run", "dev", "--", "--host"]
