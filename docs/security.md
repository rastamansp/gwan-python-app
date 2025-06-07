# Segurança

Este documento descreve as práticas e medidas de segurança implementadas no sistema.

## Autenticação

### 1. JWT (JSON Web Tokens)

```python
class JWTService:
    """Serviço para gerenciamento de tokens JWT."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, user_id: str, roles: List[str]) -> str:
        """Cria um token JWT."""
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict:
        """Verifica um token JWT."""
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
```

#### Características
- Tokens com expiração
- Assinatura digital
- Claims personalizados
- Refresh tokens

### 2. Senhas

```python
class PasswordService:
    """Serviço para gerenciamento de senhas."""

    def __init__(self, salt_rounds: int = 12):
        self.salt_rounds = salt_rounds

    def hash_password(self, password: str) -> str:
        """Gera hash da senha."""
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(self.salt_rounds)
        ).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha está correta."""
        return bcrypt.checkpw(
            password.encode(),
            hashed.encode()
        )
```

#### Características
- Hashing com bcrypt
- Salt único por usuário
- Work factor configurável
- Proteção contra timing attacks

## Autorização

### 1. RBAC (Role-Based Access Control)

```python
class RBACService:
    """Serviço para controle de acesso baseado em roles."""

    def __init__(self):
        self.roles = {
            "admin": {
                "knowledge_bases": ["create", "read", "update", "delete"],
                "files": ["create", "read", "update", "delete"],
                "users": ["create", "read", "update", "delete"]
            },
            "user": {
                "knowledge_bases": ["create", "read", "update"],
                "files": ["create", "read"],
                "users": ["read"]
            }
        }

    def has_permission(
        self,
        role: str,
        resource: str,
        action: str
    ) -> bool:
        """Verifica se uma role tem permissão."""
        if role not in self.roles:
            return False
        if resource not in self.roles[role]:
            return False
        return action in self.roles[role][resource]
```

#### Características
- Roles predefinidas
- Permissões granulares
- Fácil extensão
- Cache de permissões

### 2. Middleware de Autorização

```python
class AuthMiddleware:
    """Middleware para autorização."""

    def __init__(
        self,
        jwt_service: JWTService,
        rbac_service: RBACService
    ):
        self.jwt_service = jwt_service
        self.rbac_service = rbac_service

    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Verifica autorização da requisição."""
        token = request.headers.get("Authorization")
        if not token:
            raise UnauthorizedError()

        try:
            payload = self.jwt_service.verify_token(token)
            if not self.rbac_service.has_permission(
                payload["role"],
                request.url.path,
                request.method
            ):
                raise ForbiddenError()

            request.state.user = payload
            return await call_next(request)
        except TokenError:
            raise UnauthorizedError()
```

#### Características
- Verificação automática
- Integração com FastAPI
- Tratamento de erros
- Logging de tentativas

## Proteção de Dados

### 1. Criptografia

```python
class EncryptionService:
    """Serviço para criptografia de dados."""

    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: str) -> str:
        """Criptografa dados."""
        f = Fernet(self.key)
        return f.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados."""
        f = Fernet(self.key)
        return f.decrypt(encrypted_data.encode()).decode()
```

#### Características
- Criptografia simétrica
- Chaves seguras
- Rotação de chaves
- Backup de chaves

### 2. Sanitização

```python
class SanitizationService:
    """Serviço para sanitização de dados."""

    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome de arquivo."""
        # Remove caracteres especiais
        filename = re.sub(r'[^\w\-\.]', '_', filename)
        # Limita tamanho
        return filename[:255]

    def sanitize_html(self, html: str) -> str:
        """Sanitiza conteúdo HTML."""
        return bleach.clean(
            html,
            tags=['p', 'br', 'strong', 'em'],
            attributes={'*': ['class']}
        )
```

#### Características
- Validação de entrada
- Escape de caracteres
- Limpeza de HTML
- Prevenção de XSS

## Segurança de API

### 1. Rate Limiting

```python
class RateLimiter:
    """Implementação de rate limiting."""

    def __init__(
        self,
        redis_client: Redis,
        max_requests: int = 100,
        window: int = 3600
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window

    async def check_rate_limit(
        self,
        key: str
    ) -> bool:
        """Verifica rate limit."""
        current = await self.redis.get(key)
        if current and int(current) >= self.max_requests:
            return False

        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window)
        await pipe.execute()
        return True
```

#### Características
- Limite por IP
- Limite por usuário
- Janela deslizante
- Cache distribuído

### 2. CORS

```python
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600
)
```

#### Características
- Origem restrita
- Métodos permitidos
- Headers permitidos
- Cache de preflight

## Segurança de Infraestrutura

### 1. HTTPS

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/certs/api.example.com.crt;
    ssl_certificate_key /etc/nginx/certs/api.example.com.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Características
- TLS 1.2+
- Cipher suites seguros
- HSTS
- Certificados válidos

### 2. Firewall

```yaml
# Kubernetes Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: mongodb
    ports:
    - protocol: TCP
      port: 27017
```

#### Características
- Regras específicas
- Isolamento de rede
- Logging de tráfego
- Monitoramento

## Monitoramento de Segurança

### 1. Logging

```python
class SecurityLogger:
    """Logger para eventos de segurança."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def log_auth_attempt(
        self,
        user_id: str,
        success: bool,
        ip: str
    ) -> None:
        """Loga tentativa de autenticação."""
        self.logger.info(
            "auth_attempt",
            user_id=user_id,
            success=success,
            ip=ip,
            timestamp=datetime.utcnow().isoformat()
        )

    def log_access_denied(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> None:
        """Loga acesso negado."""
        self.logger.warning(
            "access_denied",
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.utcnow().isoformat()
        )
```

#### Características
- Logs estruturados
- Rotação de logs
- Retenção configurável
- Análise de segurança

### 2. Alertas

```python
class SecurityAlertService:
    """Serviço para alertas de segurança."""

    def __init__(
        self,
        email_service: EmailService,
        slack_service: SlackService
    ):
        self.email_service = email_service
        self.slack_service = slack_service

    async def alert_suspicious_activity(
        self,
        event: Dict
    ) -> None:
        """Envia alerta de atividade suspeita."""
        await asyncio.gather(
            self.email_service.send_alert(event),
            self.slack_service.send_alert(event)
        )
```

#### Características
- Múltiplos canais
- Priorização
- Agrupamento
- Escalação

## Backup e Recuperação

### 1. Backup

```python
class BackupService:
    """Serviço para backup de dados."""

    def __init__(
        self,
        mongodb_service: MongoDBService,
        minio_service: MinioService
    ):
        self.mongodb_service = mongodb_service
        self.minio_service = minio_service

    async def create_backup(self) -> str:
        """Cria backup dos dados."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"

        # Backup MongoDB
        await self.mongodb_service.dump(backup_id)
        # Backup MinIO
        await self.minio_service.backup(backup_id)

        return backup_id
```

#### Características
- Backup automático
- Criptografia
- Retenção configurável
- Verificação de integridade

### 2. Recuperação

```python
class RecoveryService:
    """Serviço para recuperação de dados."""

    def __init__(
        self,
        mongodb_service: MongoDBService,
        minio_service: MinioService
    ):
        self.mongodb_service = mongodb_service
        self.minio_service = minio_service

    async def restore_backup(
        self,
        backup_id: str
    ) -> None:
        """Restaura backup."""
        # Valida backup
        if not await self.validate_backup(backup_id):
            raise InvalidBackupError()

        # Restaura MongoDB
        await self.mongodb_service.restore(backup_id)
        # Restaura MinIO
        await self.minio_service.restore(backup_id)
```

#### Características
- Validação de backup
- Restauração seletiva
- Teste de recuperação
- Documentação

## Considerações de Implementação

### 1. Princípios

- Princípio do menor privilégio
- Defesa em profundidade
- Fail secure
- Segurança por padrão

### 2. Manutenção

- Atualizações de segurança
- Análise de vulnerabilidades
- Auditorias regulares
- Treinamento de equipe

### 3. Conformidade

- LGPD
- GDPR
- ISO 27001
- SOC 2

## Próximos Passos

1. **Auditoria**
   - Análise de código
   - Testes de penetração
   - Revisão de configurações
   - Relatório de segurança

2. **Melhorias**
   - Implementar 2FA
   - Adicionar WAF
   - Melhorar logging
   - Atualizar certificados

3. **Monitoramento**
   - Implementar SIEM
   - Configurar alertas
   - Análise de logs
   - Métricas de segurança

4. **Documentação**
   - Procedimentos de segurança
   - Plano de resposta a incidentes
   - Políticas de segurança
   - Guias de boas práticas 