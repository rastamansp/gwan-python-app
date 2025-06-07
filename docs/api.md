# API REST

A API REST é construída usando FastAPI e fornece endpoints para gerenciamento de knowledge bases, arquivos e usuários.

## Endpoints

### Knowledge Bases

#### Listar Knowledge Bases
```http
GET /api/v1/knowledge-bases
```

**Query Parameters:**
- `skip` (int, opcional): Número de registros para pular
- `limit` (int, opcional): Número máximo de registros
- `status` (str, opcional): Filtrar por status
- `user_id` (str, opcional): Filtrar por usuário

**Resposta:**
```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string",
      "user": {
        "id": "string",
        "name": "string",
        "email": "string"
      }
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Criar Knowledge Base
```http
POST /api/v1/knowledge-bases
```

**Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "pending",
  "created_at": "string",
  "updated_at": "string",
  "user": {
    "id": "string",
    "name": "string",
    "email": "string"
  }
}
```

#### Obter Knowledge Base
```http
GET /api/v1/knowledge-bases/{knowledge_base_id}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "user": {
    "id": "string",
    "name": "string",
    "email": "string"
  },
  "files": [
    {
      "id": "string",
      "name": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

#### Atualizar Knowledge Base
```http
PUT /api/v1/knowledge-bases/{knowledge_base_id}
```

**Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "user": {
    "id": "string",
    "name": "string",
    "email": "string"
  }
}
```

#### Excluir Knowledge Base
```http
DELETE /api/v1/knowledge-bases/{knowledge_base_id}
```

**Resposta:**
```json
{
  "message": "Knowledge base deleted successfully"
}
```

### Arquivos

#### Upload de Arquivo
```http
POST /api/v1/knowledge-bases/{knowledge_base_id}/files
```

**Body (multipart/form-data):**
- `file` (file): Arquivo a ser enviado
- `name` (string, opcional): Nome personalizado para o arquivo

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "status": "pending",
  "created_at": "string",
  "updated_at": "string",
  "knowledge_base": {
    "id": "string",
    "name": "string"
  }
}
```

#### Listar Arquivos
```http
GET /api/v1/knowledge-bases/{knowledge_base_id}/files
```

**Query Parameters:**
- `skip` (int, opcional): Número de registros para pular
- `limit` (int, opcional): Número máximo de registros
- `status` (str, opcional): Filtrar por status

**Resposta:**
```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Obter Arquivo
```http
GET /api/v1/knowledge-bases/{knowledge_base_id}/files/{file_id}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "knowledge_base": {
    "id": "string",
    "name": "string"
  },
  "processing_details": {
    "error": "string",
    "chunks": 0,
    "markdown_path": "string"
  }
}
```

#### Excluir Arquivo
```http
DELETE /api/v1/knowledge-bases/{knowledge_base_id}/files/{file_id}
```

**Resposta:**
```json
{
  "message": "File deleted successfully"
}
```

### Usuários

#### Listar Usuários
```http
GET /api/v1/users
```

**Query Parameters:**
- `skip` (int, opcional): Número de registros para pular
- `limit` (int, opcional): Número máximo de registros

**Resposta:**
```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "email": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Criar Usuário
```http
POST /api/v1/users
```

**Body:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

#### Obter Usuário
```http
GET /api/v1/users/{user_id}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "created_at": "string",
  "updated_at": "string",
  "knowledge_bases": [
    {
      "id": "string",
      "name": "string",
      "status": "string"
    }
  ]
}
```

#### Atualizar Usuário
```http
PUT /api/v1/users/{user_id}
```

**Body:**
```json
{
  "name": "string",
  "email": "string"
}
```

**Resposta:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

#### Excluir Usuário
```http
DELETE /api/v1/users/{user_id}
```

**Resposta:**
```json
{
  "message": "User deleted successfully"
}
```

## Autenticação

A API utiliza autenticação JWT (JSON Web Token).

### Login
```http
POST /api/v1/auth/login
```

**Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Resposta:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Headers:**
- `Authorization: Bearer {refresh_token}`

**Resposta:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

## Tratamento de Erros

A API retorna códigos de status HTTP apropriados e mensagens de erro detalhadas.

### Códigos de Status

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Não autorizado
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Erro de validação
- `500 Internal Server Error`: Erro interno

### Formato de Erro
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## Validação

A API utiliza Pydantic para validação de dados.

### Exemplo de Modelo
```python
from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    name: constr(min_length=3, max_length=100)
    email: EmailStr
    password: constr(min_length=8)
```

## Rate Limiting

A API implementa rate limiting para proteger contra abusos.

### Limites
- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário

### Headers de Resposta
- `X-RateLimit-Limit`: Limite total
- `X-RateLimit-Remaining`: Requisições restantes
- `X-RateLimit-Reset`: Timestamp de reset

## CORS

A API suporta CORS (Cross-Origin Resource Sharing) para requisições de diferentes origens.

### Configuração
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Documentação Interativa

A API inclui documentação interativa usando Swagger UI e ReDoc.

### URLs
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

## Monitoramento

A API inclui endpoints de monitoramento.

### Health Check
```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "version": "string",
  "timestamp": "string"
}
```

### Métricas
```http
GET /metrics
```

**Resposta:**
```json
{
  "requests_total": 0,
  "requests_in_progress": 0,
  "requests_failed": 0,
  "average_response_time": 0
}
``` 