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

- A aplicação usa a rede `gwan` existente no ambiente
- Ajuste as credenciais do banco de dados para valores seguros
- Configure o domínio correto nas labels do Traefik
- Os dados do PostgreSQL são persistidos no volume `postgres_data`
- A aplicação está configurada para usar apenas HTTPS com certificado Let's Encrypt

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

Todos os endpoints são acessíveis apenas via HTTPS:

- `https://api.gwan.com.br/`: Página inicial
- `https://api.gwan.com.br/docs`: Documentação interativa da API (Swagger UI)
- `https://api.gwan.com.br/redoc`: Documentação alternativa (ReDoc)
- `https://api.gwan.com.br/health`: Status da API
- `https://api.gwan.com.br/users`: Endpoints de usuários

## Licença

MIT 

## Como rodar o worker Knowledge Worker

O worker `knowledge_worker` é responsável pelo processamento assíncrono das mensagens da fila (RabbitMQ).

### Usando Docker

Se estiver usando Docker Compose, o serviço do worker já pode estar definido no `docker-compose.yml`. Para subir tudo:

```sh
docker-compose up --build
```

Se quiser rodar apenas o worker manualmente dentro do container, execute:

```sh
docker-compose run --rm app python src/workers/knowledge_worker.py
```

### Rodando Localmente (sem Docker)

1. **Ative o ambiente virtual:**
   ```sh
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Execute o worker:**
   ```sh
   python src/workers/knowledge_worker.py
   ```

> **Obs:** Certifique-se de que as variáveis de ambiente necessárias (como conexão com RabbitMQ, MongoDB, etc.) estejam configuradas corretamente. 