#!/bin/bash
set -e

# Função para esperar o banco de dados
wait_for_db() {
    echo "Aguardando o banco de dados..."
    for i in {1..30}; do
        if nc -z db 5432; then
            echo "Banco de dados pronto!"
            return 0
        fi
        echo "Tentativa $i de 30..."
        sleep 2
    done
    echo "Erro: Banco de dados não está disponível após 60 segundos"
    return 1
}

# Função para inicializar o banco de dados
init_db() {
    echo "Inicializando o banco de dados..."
    python -m src.database.init_db
    if [ $? -eq 0 ]; then
        echo "Banco de dados inicializado com sucesso!"
    else
        echo "Erro ao inicializar o banco de dados"
        return 1
    fi
}

# Função principal
main() {
    # Espera o banco de dados estar pronto
    wait_for_db || exit 1

    # Inicializa o banco de dados
    init_db || exit 1

    # Inicia a aplicação
    echo "Iniciando a aplicação..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000
}

# Executa a função principal
main 