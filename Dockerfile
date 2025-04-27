# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    git \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt requirements-dev.txt ./

# Instala as dependências Python
RUN pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Script de inicialização
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Comando para iniciar a aplicação
ENTRYPOINT ["/docker-entrypoint.sh"] 