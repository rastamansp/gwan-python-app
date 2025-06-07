# Padrões de Projeto

Este documento descreve os padrões de projeto utilizados no sistema, suas implementações e benefícios.

## Padrões Arquiteturais

### 1. Clean Architecture

O sistema segue os princípios da Clean Architecture, separando o código em camadas:

```
src/
├── api/          # Interface com o mundo exterior
├── core/         # Regras de negócio
└── infrastructure/ # Implementações técnicas
```

#### Benefícios
- Independência de frameworks
- Testabilidade
- Independência de UI
- Independência de banco de dados
- Independência de agentes externos

### 2. Domain-Driven Design (DDD)

Utilizamos conceitos do DDD para modelar o domínio:

#### Bounded Contexts
- Knowledge Base Management
- Document Processing
- User Management

#### Aggregates
- KnowledgeBase
- Document
- User

#### Value Objects
- FileMetadata
- ProcessingStatus
- EmbeddingVector

## Padrões de Projeto

### 1. Repository Pattern

```python
class KnowledgeBaseRepository:
    """Repository para operações com knowledge bases."""

    def __init__(self, mongodb_service: MongoDBService):
        self.collection = mongodb_service.get_collection("knowledgebases")

    async def find_by_id(self, id: str) -> Optional[Dict]:
        """Busca uma knowledge base pelo ID."""
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def update_status(self, id: str, status: str) -> None:
        """Atualiza o status de uma knowledge base."""
        await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
```

#### Benefícios
- Abstração do acesso a dados
- Centralização da lógica de persistência
- Facilita testes unitários
- Desacoplamento da lógica de negócio

### 2. Service Layer Pattern

```python
class DocumentProcessorService:
    """Serviço para processamento de documentos."""

    def __init__(
        self,
        minio_service: MinioService,
        vector_service: VectorService,
        logger: Logger
    ):
        self.minio_service = minio_service
        self.vector_service = vector_service
        self.logger = logger

    async def process_document(
        self,
        file_id: str,
        knowledge_base_id: str
    ) -> None:
        """Processa um documento."""
        # Lógica de processamento
        pass
```

#### Benefícios
- Encapsulamento da lógica de negócio
- Reutilização de código
- Facilita manutenção
- Separação de responsabilidades

### 3. Factory Pattern

```python
class ServiceFactory:
    """Factory para criação de serviços."""

    @staticmethod
    def create_mongodb_service() -> MongoDBService:
        """Cria uma instância do serviço MongoDB."""
        return MongoDBService(
            uri=settings.MONGODB_URI,
            database=settings.MONGODB_DB
        )

    @staticmethod
    def create_vector_service() -> VectorService:
        """Cria uma instância do serviço de vetores."""
        return VectorService(
            connection_string=settings.DATABASE_URL
        )
```

#### Benefícios
- Encapsula lógica de criação
- Facilita configuração
- Melhora testabilidade
- Reduz acoplamento

### 4. Strategy Pattern

```python
class DocumentProcessor:
    """Processador de documentos com estratégias diferentes."""

    def __init__(self, strategy: ProcessingStrategy):
        self.strategy = strategy

    async def process(self, document: Document) -> None:
        """Processa o documento usando a estratégia definida."""
        await self.strategy.process(document)

class PDFProcessingStrategy(ProcessingStrategy):
    """Estratégia para processamento de PDFs."""

    async def process(self, document: Document) -> None:
        # Implementação específica para PDFs
        pass

class MarkdownProcessingStrategy(ProcessingStrategy):
    """Estratégia para processamento de Markdown."""

    async def process(self, document: Document) -> None:
        # Implementação específica para Markdown
        pass
```

#### Benefícios
- Flexibilidade
- Extensibilidade
- Facilita testes
- Reduz complexidade

### 5. Observer Pattern

```python
class EventBus:
    """Barramento de eventos."""

    def __init__(self):
        self._observers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Inscreve um observador para um tipo de evento."""
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(callback)

    async def publish(self, event_type: str, data: Any) -> None:
        """Publica um evento."""
        if event_type in self._observers:
            for callback in self._observers[event_type]:
                await callback(data)
```

#### Benefícios
- Desacoplamento
- Extensibilidade
- Manutenibilidade
- Reutilização

### 6. Command Pattern

```python
class Command:
    """Interface para comandos."""

    async def execute(self) -> None:
        """Executa o comando."""
        raise NotImplementedError

class ProcessDocumentCommand(Command):
    """Comando para processar documento."""

    def __init__(
        self,
        document_id: str,
        processor: DocumentProcessor
    ):
        self.document_id = document_id
        self.processor = processor

    async def execute(self) -> None:
        """Executa o processamento do documento."""
        document = await self.get_document()
        await self.processor.process(document)
```

#### Benefícios
- Encapsula operações
- Suporta operações assíncronas
- Facilita undo/redo
- Melhora testabilidade

### 7. Decorator Pattern

```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator para retry de operações."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@retry(max_attempts=3)
async def process_document(document_id: str) -> None:
    """Processa um documento com retry."""
    # Implementação
    pass
```

#### Benefícios
- Adiciona funcionalidades dinamicamente
- Mantém código limpo
- Reutilização de código
- Facilita manutenção

### 8. Chain of Responsibility

```python
class DocumentValidator:
    """Validador de documentos em cadeia."""

    def __init__(self, next_validator: Optional['DocumentValidator'] = None):
        self.next_validator = next_validator

    async def validate(self, document: Document) -> bool:
        """Valida o documento."""
        if not self._validate(document):
            return False
        if self.next_validator:
            return await self.next_validator.validate(document)
        return True

    def _validate(self, document: Document) -> bool:
        """Implementação específica da validação."""
        raise NotImplementedError

class FileTypeValidator(DocumentValidator):
    """Valida o tipo do arquivo."""

    def _validate(self, document: Document) -> bool:
        return document.file_type in ['pdf', 'md']

class SizeValidator(DocumentValidator):
    """Valida o tamanho do arquivo."""

    def _validate(self, document: Document) -> bool:
        return document.size <= 10 * 1024 * 1024  # 10MB
```

#### Benefícios
- Desacoplamento
- Flexibilidade
- Extensibilidade
- Manutenibilidade

## Padrões de Integração

### 1. Message Queue Pattern

```python
class MessageQueue:
    """Interface para filas de mensagens."""

    async def publish(self, message: Dict) -> None:
        """Publica uma mensagem."""
        raise NotImplementedError

    async def consume(self, callback: Callable) -> None:
        """Consome mensagens."""
        raise NotImplementedError

class RabbitMQQueue(MessageQueue):
    """Implementação usando RabbitMQ."""

    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def publish(self, message: Dict) -> None:
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode()
            ),
            routing_key="processing"
        )

    async def consume(self, callback: Callable) -> None:
        channel = await self.connection.channel()
        queue = await channel.declare_queue("processing")
        await queue.consume(callback)
```

#### Benefícios
- Desacoplamento
- Escalabilidade
- Confiabilidade
- Assincronicidade

### 2. Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Implementação do Circuit Breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"

    async def execute(self, func: Callable, *args, **kwargs):
        """Executa uma função com Circuit Breaker."""
        if self.state == "open":
            if self._should_reset():
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError()

        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self._reset()
            return result
        except Exception as e:
            self._record_failure()
            raise
```

#### Benefícios
- Previne falhas em cascata
- Melhora resiliência
- Facilita recuperação
- Melhora performance

## Padrões de Teste

### 1. Test Doubles

```python
class MockMongoDBService:
    """Mock do serviço MongoDB para testes."""

    def __init__(self):
        self.collections = {}

    def get_collection(self, name: str) -> MockCollection:
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]

class MockCollection:
    """Mock de uma coleção MongoDB."""

    def __init__(self):
        self.documents = []

    async def find_one(self, query: Dict) -> Optional[Dict]:
        # Implementação do mock
        pass

    async def update_one(self, query: Dict, update: Dict) -> None:
        # Implementação do mock
        pass
```

#### Benefícios
- Isolamento de testes
- Controle de comportamento
- Verificação de interações
- Facilita testes unitários

### 2. Test Data Builder

```python
class DocumentBuilder:
    """Builder para criação de documentos de teste."""

    def __init__(self):
        self.document = {
            "id": str(ObjectId()),
            "name": "test.pdf",
            "type": "pdf",
            "size": 1024,
            "status": "pending"
        }

    def with_name(self, name: str) -> 'DocumentBuilder':
        self.document["name"] = name
        return self

    def with_type(self, type: str) -> 'DocumentBuilder':
        self.document["type"] = type
        return self

    def with_status(self, status: str) -> 'DocumentBuilder':
        self.document["status"] = status
        return self

    def build(self) -> Dict:
        return self.document.copy()
```

#### Benefícios
- Criação de dados de teste
- Legibilidade
- Manutenibilidade
- Reutilização

## Considerações de Implementação

### 1. Escolha de Padrões

- Use padrões quando fizer sentido
- Evite over-engineering
- Mantenha o código simples
- Documente decisões

### 2. Manutenção

- Mantenha padrões consistentes
- Documente implementações
- Faça code reviews
- Atualize documentação

### 3. Testes

- Teste implementações
- Use mocks apropriadamente
- Mantenha cobertura
- Automatize testes

### 4. Performance

- Monitore impacto
- Otimize quando necessário
- Use caching
- Faça profiling

## Próximos Passos

1. **Documentação**
   - Adicionar exemplos de uso
   - Criar diagramas
   - Documentar decisões

2. **Testes**
   - Aumentar cobertura
   - Adicionar testes de integração
   - Implementar testes de performance

3. **Monitoramento**
   - Adicionar métricas
   - Implementar logging
   - Configurar alertas

4. **Melhorias**
   - Revisar implementações
   - Otimizar código
   - Adicionar novos padrões 