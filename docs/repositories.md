# Repositórios

Os repositórios são responsáveis por encapsular toda a lógica de acesso aos dados, fornecendo uma interface limpa e consistente para as operações de banco de dados.

## KnowledgeBaseRepository

Responsável por todas as operações relacionadas às knowledge bases no MongoDB.

### Métodos

#### `find_by_id(knowledge_base_id: str) -> Optional[Dict[str, Any]]`
Busca uma knowledge base pelo ID.

**Parâmetros:**
- `knowledge_base_id`: ID da knowledge base

**Retorno:**
- Dicionário com os dados da knowledge base ou None se não encontrada

#### `update_status(knowledge_base_id: str, status: str, error: Optional[str] = None) -> None`
Atualiza o status de uma knowledge base.

**Parâmetros:**
- `knowledge_base_id`: ID da knowledge base
- `status`: Novo status ('completed', 'error', etc.)
- `error`: Mensagem de erro (opcional)

#### `update_after_processing(knowledge_base_id: str, bucket_file_id: str) -> None`
Atualiza a knowledge base após o processamento de um arquivo.

**Parâmetros:**
- `knowledge_base_id`: ID da knowledge base
- `bucket_file_id`: ID do arquivo processado

## BucketFileRepository

Gerencia as operações relacionadas aos arquivos do bucket no MongoDB.

### Métodos

#### `find_by_id(bucket_file_id: str) -> Optional[Dict[str, Any]]`
Busca um arquivo do bucket pelo ID.

**Parâmetros:**
- `bucket_file_id`: ID do arquivo

**Retorno:**
- Dicionário com os dados do arquivo ou None se não encontrado

#### `update_processing_status(bucket_file_id: str, status: str, error: Optional[str] = None, markdown_path: Optional[str] = None, total_chunks: Optional[int] = None) -> None`
Atualiza o status de processamento de um arquivo.

**Parâmetros:**
- `bucket_file_id`: ID do arquivo
- `status`: Novo status ('completed', 'failed', etc.)
- `error`: Mensagem de erro (opcional)
- `markdown_path`: Caminho do arquivo markdown gerado (opcional)
- `total_chunks`: Número total de chunks processados (opcional)

## UserRepository

Gerencia as operações relacionadas aos usuários no MongoDB.

### Métodos

#### `find_by_id(user_id: str) -> Optional[Dict[str, Any]]`
Busca um usuário pelo ID.

**Parâmetros:**
- `user_id`: ID do usuário

**Retorno:**
- Dicionário com os dados do usuário ou None se não encontrado

## Padrões de Projeto Utilizados

### Repository Pattern
- Encapsula a lógica de acesso aos dados
- Fornece uma interface limpa e consistente
- Facilita a troca de implementações de banco de dados
- Centraliza a lógica de queries

### Data Access Object (DAO)
- Cada repositório atua como um DAO para sua respectiva entidade
- Abstrai as operações de banco de dados
- Mantém o código de acesso a dados organizado e reutilizável

## Exemplo de Uso

```python
# Inicialização
kb_repository = KnowledgeBaseRepository(mongo_service)
file_repository = BucketFileRepository(mongo_service)
user_repository = UserRepository(mongo_service)

# Buscar knowledge base
kb = kb_repository.find_by_id("123")

# Atualizar status
kb_repository.update_status("123", "completed")

# Buscar arquivo
file_doc = file_repository.find_by_id("456")

# Atualizar status do arquivo
file_repository.update_processing_status(
    "456",
    status="completed",
    markdown_path="/path/to/file.md",
    total_chunks=10
)

# Buscar usuário
user = user_repository.find_by_id("789")
```

## Considerações de Implementação

1. **Tratamento de Erros**
   - Todos os métodos incluem tratamento de erros apropriado
   - Erros são registrados no logger
   - Exceções específicas são propagadas para camadas superiores

2. **Validação de Dados**
   - Validação de IDs antes das operações
   - Verificação de campos obrigatórios
   - Tipagem forte com type hints

3. **Performance**
   - Uso de índices apropriados no MongoDB
   - Operações em lote quando possível
   - Cache de consultas frequentes (quando implementado)

4. **Manutenibilidade**
   - Código documentado com docstrings
   - Métodos pequenos e focados
   - Separação clara de responsabilidades 