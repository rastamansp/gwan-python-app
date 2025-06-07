# Workers

Os workers são responsáveis pelo processamento assíncrono de tarefas, consumindo mensagens das filas do RabbitMQ e executando as operações necessárias.

## Knowledge Worker

O `knowledge_worker.py` é responsável pelo processamento de documentos e geração de embeddings.

### Fluxo de Processamento

1. **Recebimento da Mensagem**
   ```json
   {
     "knowledgeBaseId": "string",
     "userId": "string",
     "bucketFileId": "string"
   }
   ```

2. **Validação**
   - Verifica campos obrigatórios
   - Valida existência da knowledge base
   - Valida existência do usuário
   - Valida existência do arquivo

3. **Processamento**
   - Download do arquivo do MinIO
   - Conversão para markdown
   - Divisão em chunks
   - Geração de embeddings
   - Armazenamento no PostgreSQL

4. **Atualização de Status**
   - Atualiza status do arquivo
   - Atualiza status da knowledge base
   - Registra erros se houver

### Configuração

```python
# Variáveis de ambiente necessárias
RABBITMQ_HOST=rabbitmq.example.com.br
RABBITMQ_PORT=5672
RABBITMQ_USER=root
RABBITMQ_PASSWORD=password
MONGODB_URI=mongodb://example.com.br:27017
MONGODB_DB=example
DATABASE_URL=postgresql://*****:*****@db:5432/example
```

### Execução

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Executar worker
python src/workers/knowledge_worker.py
```

## PDF Worker

O `pdf_worker.py` é responsável pelo processamento específico de arquivos PDF.

### Fluxo de Processamento

1. **Recebimento da Mensagem**
   ```json
   {
     "file_data": "base64",
     "prompt": "string",
     "filename": "string",
     "user_id": "string",
     "processing_id": "string"
   }
   ```

2. **Processamento**
   - Decodifica dados do arquivo
   - Processa o PDF
   - Gera markdown
   - Atualiza status no banco

### Configuração

```python
# Variáveis de ambiente necessárias
RABBITMQ_HOST=rabbitmq.gwan.com.br
RABBITMQ_PORT=5672
RABBITMQ_USER=root
RABBITMQ_PASSWORD=pazdeDeus2025
DATABASE_URL=postgresql://gwan_user:gwan_password@db:5432/gwan_db
```

### Execução

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Executar worker
python src/workers/pdf_worker.py
```

## Padrões de Projeto Utilizados

### Consumer Pattern
- Consome mensagens de forma assíncrona
- Processa mensagens em background
- Gerencia reconexões e retries

### Worker Pattern
- Executa tarefas em background
- Gerencia recursos (conexões, sessões)
- Implementa mecanismos de retry

## Tratamento de Erros

1. **Erros de Conexão**
   - Reconexão automática com RabbitMQ
   - Retry com backoff exponencial
   - Logging de erros de conexão

2. **Erros de Processamento**
   - Rollback de transações
   - Atualização de status
   - Notificação de erros
   - Retry se apropriado

3. **Erros de Validação**
   - Rejeição de mensagens inválidas
   - Logging detalhado
   - Métricas de mensagens rejeitadas

## Monitoramento

1. **Métricas**
   - Mensagens processadas
   - Tempo de processamento
   - Taxa de erros
   - Uso de recursos

2. **Logs**
   - Início/fim de processamento
   - Erros e exceções
   - Status de operações
   - Performance

3. **Health Checks**
   - Status do worker
   - Conexões ativas
   - Fila de mensagens
   - Recursos do sistema

## Exemplo de Uso com Docker

```yaml
# docker-compose.yml
services:
  knowledge_worker:
    build: .
    command: python src/workers/knowledge_worker.py
    environment:
      - RABBITMQ_HOST=rabbitmq.gwan.com.br
      - RABBITMQ_PORT=5672
      - RABBITMQ_USER=root
      - RABBITMQ_PASSWORD=pazdeDeus2025
      - MONGODB_URI=mongodb://mongodb.gwan.com.br:27017
      - MONGODB_DB=gwan
      - DATABASE_URL=postgresql://gwan_user:gwan_password@db:5432/gwan_db
    depends_on:
      - db
      - rabbitmq
    networks:
      - gwan
```

## Considerações de Implementação

1. **Escalabilidade**
   - Múltiplas instâncias do worker
   - Balanceamento de carga
   - Gerenciamento de recursos

2. **Performance**
   - Processamento em lote
   - Conexões persistentes
   - Cache quando apropriado

3. **Manutenibilidade**
   - Código modular
   - Logs estruturados
   - Monitoramento abrangente

4. **Segurança**
   - Validação de mensagens
   - Sanitização de dados
   - Controle de acesso
   - Proteção de credenciais 