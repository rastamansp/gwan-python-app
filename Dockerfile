# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Instala o driver do PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && pip install psycopg2-binary \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copia o código da aplicação
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 