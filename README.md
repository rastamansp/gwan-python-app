# Gwan Python App

Aplicação Python para a Gwan Company.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- virtualenv ou venv (para ambiente virtual)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/rastamansp/gwan-python-app.git
cd gwan-python-app
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Estrutura do Projeto

```
gwan-python-app/
├── src/                    # Código fonte
│   ├── api/               # Endpoints da API
│   ├── core/              # Lógica de negócios
│   ├── database/          # Configuração do banco de dados
│   └── models/            # Modelos de dados
├── tests/                 # Testes
├── docs/                  # Documentação
├── .env.example          # Exemplo de variáveis de ambiente
├── requirements.txt      # Dependências do projeto
└── README.md            # Este arquivo
```

## Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
uvicorn src.main:app --reload
```

## Testes

Para executar os testes:

```bash
pytest
```

## Formatação de Código

Para formatar o código:

```bash
black .
isort .
flake8
```

## Documentação

A documentação está disponível em Markdown na pasta `docs/`. Para gerar a documentação HTML:

```bash
mkdocs serve
```

## Licença

MIT 