# Guia de Desenvolvimento

Este guia fornece instruções detalhadas para desenvolvedores que desejam contribuir com o projeto.

## Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.9+
- Git
- Docker e Docker Compose
- MongoDB
- PostgreSQL 13+ com pgvector
- MinIO
- RabbitMQ

### Configuração Inicial

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/gwan/gwan-python-app.git
   cd gwan-python-app
   ```

2. **Crie um Ambiente Virtual**
   ```bash
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale as Dependências**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure as Variáveis de Ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Inicie os Serviços com Docker**
   ```bash
   docker-compose up -d
   ```

## Estrutura do Projeto

```
gwan-python-app/
├── src/
│   ├── api/                    # API REST
│   │   ├── v1/                # Versionamento da API
│   │   ├── dependencies/      # Injeção de dependências
│   │   ├── middleware/        # Middlewares
│   │   └── models/           # Schemas Pydantic
│   ├── core/                  # Lógica de negócio
│   │   ├── usecases/         # Casos de uso
│   │   ├── services/         # Serviços
│   │   ├── repositories/     # Repositórios
│   │   └── models/          # Modelos de domínio
│   ├── infrastructure/        # Infraestrutura
│   │   ├── config/          # Configurações
│   │   ├── database/        # Conexões
│   │   └── logging/         # Logging
│   └── workers/              # Workers
├── tests/                     # Testes
├── docs/                      # Documentação
└── scripts/                   # Scripts utilitários
```

## Convenções de Código

### Python

- Siga o [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Documente funções e classes com docstrings
- Mantenha funções pequenas e focadas
- Use nomes descritivos

### Exemplo de Código

```python
from typing import Optional, List
from datetime import datetime

class KnowledgeBase:
    """Representa uma base de conhecimento."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Inicializa uma nova base de conhecimento.

        Args:
            name: Nome da base de conhecimento
            description: Descrição opcional
            user_id: ID do usuário dono
        """
        self.name = name
        self.description = description
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
```

## Testes

### Tipos de Testes

1. **Testes Unitários**
   - Testam unidades individuais
   - Localizados em `tests/unit/`
   - Usam pytest

2. **Testes de Integração**
   - Testam integração entre componentes
   - Localizados em `tests/integration/`
   - Usam pytest com fixtures

3. **Testes E2E**
   - Testam fluxos completos
   - Localizados em `tests/e2e/`
   - Usam pytest com containers

### Executando Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Com cobertura
pytest --cov=src tests/

# Com relatório HTML
pytest --cov=src --cov-report=html tests/
```

### Exemplo de Teste

```python
import pytest
from datetime import datetime
from src.core.models.knowledge_base import KnowledgeBase

def test_knowledge_base_creation():
    """Testa a criação de uma base de conhecimento."""
    # Arrange
    name = "Test Base"
    description = "Test Description"
    user_id = "user123"

    # Act
    kb = KnowledgeBase(
        name=name,
        description=description,
        user_id=user_id
    )

    # Assert
    assert kb.name == name
    assert kb.description == description
    assert kb.user_id == user_id
    assert isinstance(kb.created_at, datetime)
    assert kb.created_at == kb.updated_at
```

## Logging

### Configuração

```python
import structlog

logger = structlog.get_logger()

# Uso
logger.info(
    "event_name",
    user_id="123",
    action="create",
    resource="knowledge_base"
)
```

### Níveis de Log

- `DEBUG`: Informações detalhadas
- `INFO`: Eventos normais
- `WARNING`: Avisos
- `ERROR`: Erros
- `CRITICAL`: Erros críticos

## Mensageria

### Publicando Mensagens

```python
from src.infrastructure.messaging.rabbitmq import RabbitMQService

async def publish_message():
    service = RabbitMQService()
    await service.publish(
        exchange="knowledge",
        routing_key="processing",
        message={
            "knowledge_base_id": "123",
            "file_id": "456"
        }
    )
```

### Consumindo Mensagens

```python
from src.infrastructure.messaging.rabbitmq import RabbitMQService

async def process_message(message):
    # Processa a mensagem
    pass

async def start_consumer():
    service = RabbitMQService()
    await service.consume(
        queue="knowledge.processing",
        callback=process_message
    )
```

## Banco de Dados

### MongoDB

```python
from src.infrastructure.database.mongodb import MongoDBService

async def example_mongodb():
    service = MongoDBService()
    collection = service.get_collection("knowledgebases")
    
    # Inserir
    result = await collection.insert_one({
        "name": "Test Base",
        "status": "active"
    })
    
    # Buscar
    doc = await collection.find_one({"_id": result.inserted_id})
```

### PostgreSQL

```python
from src.infrastructure.database.postgresql import PostgreSQLService

async def example_postgresql():
    service = PostgreSQLService()
    
    # Executar query
    async with service.get_connection() as conn:
        result = await conn.execute(
            "SELECT * FROM document_embeddings WHERE id = $1",
            "123"
        )
        row = await result.fetchone()
```

## Armazenamento

### MinIO

```python
from src.infrastructure.storage.minio import MinioService

async def example_minio():
    service = MinioService()
    
    # Upload
    await service.upload_file(
        bucket="documents",
        file_path="local/path/file.pdf",
        object_name="remote/path/file.pdf"
    )
    
    # Download
    await service.download_file(
        bucket="documents",
        object_name="remote/path/file.pdf",
        file_path="local/path/downloaded.pdf"
    )
```

## Contribuição

### Processo de Desenvolvimento

1. **Crie uma Branch**
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Desenvolva**
   - Siga as convenções de código
   - Adicione testes
   - Atualize documentação

3. **Teste**
   ```bash
   pytest
   flake8
   mypy
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   ```

5. **Push**
   ```bash
   git push origin feature/nova-funcionalidade
   ```

6. **Pull Request**
   - Crie PR no GitHub
   - Aguarde revisão
   - Faça ajustes se necessário

### Convenções de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas gerais

### Exemplo
```
feat: adiciona processamento de PDF

- Implementa conversão PDF para markdown
- Adiciona worker para processamento
- Inclui testes unitários e de integração
```

## Troubleshooting

### Problemas Comuns

1. **Erro de Conexão com MongoDB**
   - Verifique se o MongoDB está rodando
   - Confira as credenciais no `.env`
   - Verifique a rede

2. **Erro de Conexão com PostgreSQL**
   - Verifique se o PostgreSQL está rodando
   - Confira as credenciais no `.env`
   - Verifique se o pgvector está instalado

3. **Erro no Worker**
   - Verifique os logs
   - Confira a conexão com RabbitMQ
   - Verifique as permissões do MinIO

### Logs

- **API**: `logs/api.log`
- **Worker**: `logs/worker.log`
- **Docker**: `docker-compose logs`

## Recursos Adicionais

- [Documentação da API](api.md)
- [Arquitetura](architecture.md)
- [Padrões de Projeto](patterns.md)
- [Guia de Deploy](deployment.md) 