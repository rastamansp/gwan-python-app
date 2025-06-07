# Testes

Este documento descreve a estratégia de testes implementada no sistema.

## Visão Geral

O sistema implementa uma estratégia abrangente de testes para garantir:

- Qualidade do código
- Funcionalidade correta
- Performance adequada
- Segurança
- Manutenibilidade

## Tipos de Testes

### 1. Testes Unitários

#### Estrutura
```
tests/
├── unit/
│   ├── core/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── usecases/
│   └── api/
│       ├── endpoints/
│       └── middleware/
```

#### Exemplo de Teste
```python
class TestDocumentProcessorService:
    """Testes do serviço de processamento de documentos."""

    @pytest.fixture
    def service(self):
        """Fixture do serviço."""
        return DocumentProcessorService(
            minio_service=MockMinioService(),
            vector_service=MockVectorService(),
            logger=MockLogger()
        )

    async def test_process_document_success(self, service):
        """Testa processamento bem-sucedido."""
        # Arrange
        document_id = "doc-123"
        content = "Test content"

        # Act
        result = await service.process_document(document_id, content)

        # Assert
        assert result.status == "processed"
        assert result.embeddings_count > 0

    async def test_process_document_invalid_content(self, service):
        """Testa processamento com conteúdo inválido."""
        # Arrange
        document_id = "doc-123"
        content = ""

        # Act & Assert
        with pytest.raises(InvalidContentError):
            await service.process_document(document_id, content)
```

#### Cobertura
- Funções e métodos
- Classes
- Edge cases
- Tratamento de erros

### 2. Testes de Integração

#### Estrutura
```
tests/
├── integration/
│   ├── api/
│   │   ├── knowledge_bases/
│   │   ├── documents/
│   │   └── users/
│   └── workers/
│       ├── knowledge_worker/
│       └── pdf_worker/
```

#### Exemplo de Teste
```python
class TestKnowledgeBaseAPI:
    """Testes de integração da API de knowledge bases."""

    @pytest.fixture
    async def client(self):
        """Fixture do cliente HTTP."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    async def test_create_knowledge_base(self, client):
        """Testa criação de knowledge base."""
        # Arrange
        data = {
            "name": "Test KB",
            "description": "Test description"
        }

        # Act
        response = await client.post(
            "/api/v1/knowledge-bases",
            json=data,
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert "id" in result

    async def test_create_knowledge_base_unauthorized(self, client):
        """Testa criação sem autenticação."""
        # Arrange
        data = {
            "name": "Test KB",
            "description": "Test description"
        }

        # Act
        response = await client.post(
            "/api/v1/knowledge-bases",
            json=data
        )

        # Assert
        assert response.status_code == 401
```

#### Cobertura
- Endpoints da API
- Fluxos completos
- Integração com serviços
- Autenticação/Autorização

### 3. Testes E2E

#### Estrutura
```
tests/
├── e2e/
│   ├── scenarios/
│   │   ├── document_processing/
│   │   └── knowledge_base_management/
│   └── fixtures/
│       ├── data/
│       └── services/
```

#### Exemplo de Teste
```python
class TestDocumentProcessingE2E:
    """Testes E2E de processamento de documentos."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup do ambiente de teste."""
        # Inicia serviços
        await start_services()
        # Limpa dados
        await clean_test_data()
        yield
        # Limpa ambiente
        await stop_services()

    async def test_document_processing_flow(self):
        """Testa fluxo completo de processamento."""
        # Arrange
        kb = await create_test_knowledge_base()
        file_path = "tests/fixtures/data/test.pdf"

        # Act
        # 1. Upload do documento
        doc = await upload_document(kb.id, file_path)
        assert doc.status == "uploaded"

        # 2. Aguarda processamento
        doc = await wait_for_processing(doc.id)
        assert doc.status == "processed"

        # 3. Verifica embeddings
        embeddings = await get_document_embeddings(doc.id)
        assert len(embeddings) > 0

        # 4. Testa busca
        results = await search_knowledge_base(kb.id, "test query")
        assert len(results) > 0
```

#### Cobertura
- Fluxos de negócio
- Cenários completos
- Performance
- Concorrência

### 4. Testes de Performance

#### Estrutura
```
tests/
├── performance/
│   ├── load/
│   │   ├── api/
│   │   └── workers/
│   └── stress/
│       ├── concurrent/
│       └── memory/
```

#### Exemplo de Teste
```python
class TestAPIPerformance:
    """Testes de performance da API."""

    @pytest.mark.benchmark
    async def test_document_upload_performance(self, benchmark):
        """Testa performance de upload."""
        # Arrange
        client = await get_test_client()
        file_path = "tests/fixtures/data/large.pdf"

        # Act & Assert
        result = await benchmark(
            upload_document,
            client,
            file_path
        )
        assert result.duration < 5.0  # 5 segundos

    @pytest.mark.load
    async def test_concurrent_uploads(self):
        """Testa uploads concorrentes."""
        # Arrange
        client = await get_test_client()
        file_paths = [
            f"tests/fixtures/data/doc_{i}.pdf"
            for i in range(10)
        ]

        # Act
        start_time = time.time()
        results = await asyncio.gather(*[
            upload_document(client, path)
            for path in file_paths
        ])
        duration = time.time() - start_time

        # Assert
        assert all(r.status == "uploaded" for r in results)
        assert duration < 30.0  # 30 segundos
```

#### Métricas
- Tempo de resposta
- Throughput
- Uso de recursos
- Escalabilidade

### 5. Testes de Segurança

#### Estrutura
```
tests/
├── security/
│   ├── auth/
│   ├── api/
│   └── data/
```

#### Exemplo de Teste
```python
class TestAPISecurity:
    """Testes de segurança da API."""

    async def test_jwt_validation(self, client):
        """Testa validação de JWT."""
        # Arrange
        invalid_tokens = [
            "invalid",
            "expired_token",
            "malformed_token"
        ]

        # Act & Assert
        for token in invalid_tokens:
            response = await client.get(
                "/api/v1/knowledge-bases",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 401

    async def test_rate_limiting(self, client):
        """Testa rate limiting."""
        # Arrange
        requests = 100

        # Act
        responses = await asyncio.gather(*[
            client.get("/api/v1/knowledge-bases")
            for _ in range(requests)
        ])

        # Assert
        blocked = sum(1 for r in responses if r.status_code == 429)
        assert blocked > 0
```

#### Cobertura
- Autenticação
- Autorização
- Rate limiting
- Validação de dados

## Ferramentas

### 1. Frameworks

#### pytest
```yaml
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Testes unitários
    integration: Testes de integração
    e2e: Testes end-to-end
    performance: Testes de performance
    security: Testes de segurança
```

#### Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_knowledge_bases(self):
        self.client.get("/api/v1/knowledge-bases")

    @task
    def upload_document(self):
        with open("test.pdf", "rb") as f:
            self.client.post(
                "/api/v1/documents",
                files={"file": f}
            )
```

### 2. Mocks e Fixtures

#### Exemplos
```python
@pytest.fixture
def mock_mongodb():
    """Mock do MongoDB."""
    return MockMongoDBService()

@pytest.fixture
def mock_minio():
    """Mock do MinIO."""
    return MockMinioService()

@pytest.fixture
def test_document():
    """Fixture de documento de teste."""
    return {
        "id": "doc-123",
        "name": "test.pdf",
        "content": "Test content",
        "status": "pending"
    }
```

### 3. Cobertura

#### Configuração
```yaml
# .coveragerc
[run]
source = src
omit =
    tests/*
    */__init__.py
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

## CI/CD

### 1. Pipeline de Testes

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017
      postgres:
        image: postgres:latest
        env:
          POSTGRES_DB: test_db
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### 2. Relatórios

#### Cobertura
- Relatório HTML
- Relatório XML
- Badge no README
- Integração com Codecov

#### Testes
- Relatório JUnit
- Logs detalhados
- Screenshots (E2E)
- Vídeos (E2E)

## Considerações

### 1. Boas Práticas

- Testes isolados
- Dados de teste limpos
- Mocks apropriados
- Assertions claros
- Nomes descritivos

### 2. Manutenção

- Atualização de testes
- Limpeza de dados
- Documentação
- Revisão de cobertura

### 3. Performance

- Execução paralela
- Cache de fixtures
- Otimização de mocks
- Limpeza eficiente

## Próximos Passos

1. **Melhorias**
   - Aumentar cobertura
   - Adicionar testes de carga
   - Melhorar relatórios
   - Automatizar mais cenários

2. **Integração**
   - Adicionar testes de UI
   - Implementar testes de API
   - Melhorar testes E2E
   - Adicionar testes de segurança

3. **Infraestrutura**
   - Otimizar pipeline
   - Melhorar ambiente
   - Adicionar ferramentas
   - Automatizar deploy

4. **Documentação**
   - Guias de teste
   - Exemplos
   - Troubleshooting
   - Treinamento 