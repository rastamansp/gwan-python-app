# Serviços

Os serviços encapsulam a lógica de negócios da aplicação, coordenando as operações entre diferentes componentes e repositórios.

## DocumentProcessorService

Responsável pelo processamento de documentos, incluindo download, conversão e preparação para geração de embeddings.

### Métodos

#### `download_and_process_file(bucket: str, filename: str, original_name: str) -> tuple[str, str]`
Baixa um arquivo do MinIO, processa e retorna o conteúdo em markdown.

**Parâmetros:**
- `bucket`: Nome do bucket no MinIO
- `filename`: Nome do arquivo no bucket
- `original_name`: Nome original do arquivo

**Retorno:**
- Tupla contendo (caminho do arquivo markdown, conteúdo markdown)

#### `split_content(content: str, max_chunk_size: int = 1000) -> List[str]`
Divide o conteúdo em chunks menores para processamento.

**Parâmetros:**
- `content`: Conteúdo a ser dividido
- `max_chunk_size`: Tamanho máximo de cada chunk (padrão: 1000)

**Retorno:**
- Lista de chunks de texto

#### `prepare_metadata(user_id: str, user_name: str, user_email: str, file_name: str, file_id: str, knowledge_base_id: str, knowledge_base_name: str, markdown_path: str, bucket_name: str, original_file_name: str) -> Dict[str, Any]`
Prepara os metadados para o processamento do documento.

**Parâmetros:**
- Vários campos de metadados necessários para o processamento

**Retorno:**
- Dicionário com os metadados formatados

## VectorService

Gerencia as operações relacionadas aos embeddings vetoriais.

### Métodos

#### `create_embedding(content: str) -> List[float]`
Cria um embedding para o conteúdo fornecido.

**Parâmetros:**
- `content`: Texto para gerar o embedding

**Retorno:**
- Lista de floats representando o embedding

#### `store_embedding(knowledge_base_id: str, user_id: str, bucket_file_id: str, chunk_index: int, content: str, meta: Optional[Dict[str, Any]] = None) -> DocumentEmbedding`
Armazena um embedding no banco de dados.

**Parâmetros:**
- `knowledge_base_id`: ID da knowledge base
- `user_id`: ID do usuário
- `bucket_file_id`: ID do arquivo
- `chunk_index`: Índice do chunk
- `content`: Conteúdo do chunk
- `meta`: Metadados adicionais (opcional)

**Retorno:**
- Objeto DocumentEmbedding criado

#### `store_embeddings_batch(embeddings_data: list, batch_size: int = 2) -> List[DocumentEmbedding]`
Armazena múltiplos embeddings em lote.

**Parâmetros:**
- `embeddings_data`: Lista de dicionários com dados dos embeddings
- `batch_size`: Tamanho do lote (padrão: 2)

**Retorno:**
- Lista de DocumentEmbedding criados

## RabbitMQService

Gerencia a comunicação com o RabbitMQ para processamento assíncrono.

### Métodos

#### `consume(callback: Callable) -> None`
Inicia o consumo de mensagens da fila.

**Parâmetros:**
- `callback`: Função a ser chamada para cada mensagem recebida

## MinioService

Gerencia as operações de armazenamento de arquivos no MinIO.

### Métodos

#### `upload_file(bucket: str, file_path: str, object_name: Optional[str] = None) -> str`
Faz upload de um arquivo para o MinIO.

**Parâmetros:**
- `bucket`: Nome do bucket
- `file_path`: Caminho do arquivo local
- `object_name`: Nome do objeto no MinIO (opcional)

**Retorno:**
- Nome do objeto no MinIO

#### `download_file(bucket: str, object_name: str, file_path: str) -> None`
Baixa um arquivo do MinIO.

**Parâmetros:**
- `bucket`: Nome do bucket
- `object_name`: Nome do objeto
- `file_path`: Caminho local para salvar o arquivo

## Padrões de Projeto Utilizados

### Service Layer Pattern
- Encapsula a lógica de negócios
- Coordena operações entre diferentes componentes
- Fornece uma interface limpa para as camadas superiores

### Facade Pattern
- Simplifica a interface com sistemas externos
- Abstrai a complexidade das operações
- Centraliza a configuração dos serviços

## Exemplo de Uso

```python
# Inicialização dos serviços
doc_processor = DocumentProcessorService(minio_service, logger)
vector_service = VectorService(db_session)
rabbitmq_service = RabbitMQService(host, port, user, password, queue)

# Processamento de documento
markdown_path, content = doc_processor.download_and_process_file(
    bucket="datasets",
    filename="doc.pdf",
    original_name="documento.pdf"
)

# Geração de embeddings
chunks = doc_processor.split_content(content)
metadata = doc_processor.prepare_metadata(
    user_id="123",
    user_name="João",
    # ... outros metadados
)

# Armazenamento em lote
vector_service.store_embeddings_batch(
    embeddings_data=[
        {
            "knowledgeBaseId": "kb123",
            "userId": "user123",
            "content": chunk,
            "meta": metadata
        }
        for chunk in chunks
    ],
    batch_size=2
)

# Consumo de mensagens
rabbitmq_service.consume(process_message_callback)
```

## Considerações de Implementação

1. **Tratamento de Erros**
   - Tratamento específico para cada tipo de erro
   - Retry em operações críticas
   - Logging detalhado de erros

2. **Performance**
   - Processamento em lote quando possível
   - Cache de embeddings
   - Conexões persistentes com serviços externos

3. **Segurança**
   - Validação de dados de entrada
   - Sanitização de nomes de arquivos
   - Controle de acesso baseado em usuário

4. **Manutenibilidade**
   - Código modular e bem documentado
   - Testes unitários para cada serviço
   - Monitoramento de performance 