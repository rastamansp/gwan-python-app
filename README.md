# Gwan Python App

Aplicação Python para a Gwan Company.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- virtualenv ou venv (para ambiente virtual)
- Docker e Docker Compose (para implantação em container)

## Instalação Local

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
├── docker-compose.yml    # Configuração do Docker Compose
├── Dockerfile           # Configuração do container da aplicação
└── README.md            # Este arquivo
```

## Desenvolvimento Local

Para iniciar o servidor de desenvolvimento:

```bash
uvicorn src.main:app --reload
```

## Implantação com Docker

### Implantação Local com Docker Compose

1. Construa e inicie os containers:
```bash
docker-compose up -d --build
```

2. Verifique os logs:
```bash
docker-compose logs -f
```

3. Para parar os containers:
```bash
docker-compose down
```

### Implantação na VPS (Hostinger) com Portainer

1. Acesse o Portainer na sua VPS
2. Vá para "Stacks" e clique em "Add stack"
3. Dê um nome para a stack (ex: "gwan-python-app")
4. Cole o conteúdo do arquivo `docker-compose.yml`
5. Ajuste as variáveis de ambiente conforme necessário:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `DATABASE_URL`
6. Configure o domínio no Traefik (atualmente definido como `api.gwan.com.br`)
7. Clique em "Deploy the stack"

#### Observações para Implantação

- Certifique-se de que a rede `gwan-network` existe na VPS
- Ajuste as credenciais do banco de dados para valores seguros
- Configure o domínio correto nas labels do Traefik
- Os dados do PostgreSQL são persistidos no volume `postgres_data`

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

## Endpoints da API

- `/`: Página inicial
- `/docs`: Documentação interativa da API (Swagger UI)
- `/redoc`: Documentação alternativa (ReDoc)
- `/health`: Status da API
- `/users`: Endpoints de usuários

## Licença

MIT 