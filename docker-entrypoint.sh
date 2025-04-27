#!/bin/bash

# Espera o banco de dados estar pronto
echo "Aguardando o banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Banco de dados pronto!"

# Inicializa o banco de dados
echo "Inicializando o banco de dados..."
python -m src.database.init_db

# Inicia a aplicação
echo "Iniciando a aplicação..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 