# Gwan Python App

Aplicação Python para processamento e gerenciamento de conhecimento baseado em documentos.

## 🚀 Visão Geral

O Gwan Python App é uma aplicação que processa documentos (PDFs) e os converte em conhecimento estruturado através de embeddings vetoriais. A aplicação utiliza uma arquitetura baseada em microserviços, com workers assíncronos para processamento de documentos e uma API REST para gerenciamento.

### Principais Funcionalidades

- Processamento assíncrono de documentos PDF
- Conversão de PDF para Markdown
- Geração de embeddings vetoriais
- Armazenamento em banco de dados vetorial
- API REST para gerenciamento
- Sistema de filas para processamento assíncrono

## 🏗️ Arquitetura

### Componentes Principais

1. **API REST (FastAPI)**
   - Endpoints para gerenciamento de knowledge bases
   - Autenticação e autorização
   - Upload e download de documentos

2. **Workers**
   - `knowledge_worker.py`: Processa documentos e gera embeddings
   - `pdf_worker.py`: Processamento específico de PDFs

3. **Serviços**
   - `VectorService`: Gerenciamento de embeddings
   - `MongoService`: Operações no MongoDB
   - `MinioService`: Armazenamento de arquivos
   - `RabbitmqService`: Gerenciamento de filas

4. **Repositórios**
   - `KnowledgeBaseRepository`: Operações com knowledge bases
   - `BucketFileRepository`: Gerenciamento de arquivos
   - `UserRepository`: Operações com usuários

### Diagrama de Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    API      │     │   Workers   │     │  Serviços   │
│  (FastAPI)  │◄────┤  (RabbitMQ) │◄────┤  (MongoDB)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  MinIO      │     │ PostgreSQL  │     │  MongoDB    │
│ (Arquivos)  │     │(Embeddings) │     │ (Metadata)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **FastAPI**: Framework web
- **MongoDB**: Banco de dados para metadados
- **PostgreSQL**: Banco de dados vetorial
- **MinIO**: Armazenamento de arquivos
- **RabbitMQ**: Sistema de mensageria
- **Docling**: Processamento de documentos
- **OpenAI**: Geração de embeddings

## 📦 Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rastamansp/gwan-python-app.git
   cd gwan-python-app
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
   # Configurações do Banco de Dados
   DATABASE_URL=postgresql://gwan_user:gwan_password@db:5432/gwan_db
   POSTGRES_USER=gwan_user
   POSTGRES_PASSWORD=gwan_password
   POSTGRES_DB=gwan_db

   # Configurações do RabbitMQ
   RABBITMQ_HOST=rabbitmq.gwan.com.br
   RABBITMQ_PORT=5672
   RABBITMQ_USER=root
   RABBITMQ_PASSWORD=pazdeDeus2025

   # Configurações do MongoDB
   MONGODB_URI=mongodb://mongodb.gwan.com.br:27017
   MONGODB_DB=gwan

   # Configurações do MinIO
   MINIO_ENDPOINT=minio.gwan.com.br
   MINIO_ACCESS_KEY=admin
   MINIO_SECRET_KEY=pazdeDeus@2025
   MINIO_SECURE=true
   MINIO_TMP_FOLDER=tmp

   # Configurações da API
   API_V1_STR=/v1
   PROJECT_NAME=Gwan Python App
   DEBUG=false

   # Configurações de Segurança
   SECRET_KEY=sua_chave_secreta_aqui
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Configurações do OpenAI
   OPENAI_API_KEY=sua_chave_api_aqui
   ```

## 🚀 Executando a Aplicação

### API REST

```bash
uvicorn src.main:app --reload --port 8000
```

### Workers

```bash
# Worker de Knowledge Base
python src/workers/knowledge_worker.py

# Worker de PDF
python src/workers/pdf_worker.py
```

### Docker Compose

```bash
docker-compose up -d
```

## 📚 Documentação da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=src tests/
```

## 📁 Estrutura do Projeto

```
gwan-python-app/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── dependencies/
│   ├── core/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── usecases/
│   ├── infrastructure/
│   │   ├── config/
│   │   └── logging/
│   ├── models/
│   ├── workers/
│   └── main.py
├── tests/
├── docs/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📫 Contato

Rastaman - [@rastamansp](https://github.com/rastamansp)

Link do Projeto: [https://github.com/rastamansp/gwan-python-app](https://github.com/rastamansp/gwan-python-app) 