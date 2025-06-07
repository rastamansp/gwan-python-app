# Monitoramento

Este documento descreve a estratégia de monitoramento implementada no sistema.

## Visão Geral

O sistema implementa um conjunto abrangente de ferramentas e práticas de monitoramento para garantir:

- Disponibilidade e performance da aplicação
- Saúde dos serviços e infraestrutura
- Detecção e alerta de problemas
- Análise de tendências e capacidade
- Conformidade e segurança

## Arquitetura de Monitoramento

```
                    +----------------+
                    |    Grafana     |
                    +----------------+
                           ↑
                           |
                    +----------------+
                    |   Prometheus   |
                    +----------------+
                           ↑
                           |
+----------------+  +----------------+  +----------------+
|      API       |  |    Workers     |  |  Infraestrutura|
+----------------+  +----------------+  +----------------+
                           ↑
                           |
                    +----------------+
                    |     Jaeger     |
                    +----------------+
                           ↑
                           |
                    +----------------+
                    |   Elasticsearch |
                    +----------------+
```

## Métricas

### 1. Métricas da Aplicação

#### Contadores
- Total de requisições HTTP por endpoint
- Total de erros por tipo
- Total de documentos processados
- Total de operações de banco de dados

#### Histogramas
- Duração das requisições HTTP
- Tempo de processamento de documentos
- Latência de operações de banco
- Tamanho de payloads

#### Gauges
- Conexões ativas
- Tamanho de filas
- Uso de memória
- Threads ativas

### 2. Métricas de Infraestrutura

#### Sistema
- CPU (uso, load, cores)
- Memória (total, usado, livre)
- Disco (espaço, IOPS, latência)
- Rede (tráfego, conexões, erros)

#### Containers
- Uso de recursos
- Restarts
- Health checks
- Logs

## Logging

### 1. Estrutura de Logs

#### Campos Padrão
- Timestamp (ISO 8601)
- Nível (INFO, WARN, ERROR, etc)
- Logger name
- Thread/Process ID
- Request ID
- User ID (quando aplicável)
- Contexto (método, endpoint, etc)

#### Exemplo de Log
```json
{
  "timestamp": "2024-03-20T10:15:30.123Z",
  "level": "INFO",
  "logger": "api.request",
  "request_id": "req-123",
  "user_id": "user-456",
  "method": "POST",
  "endpoint": "/api/v1/documents",
  "duration_ms": 150,
  "status_code": 201
}
```

### 2. Rotação e Retenção

#### Políticas
- Rotação diária
- Compressão após 7 dias
- Retenção por 30 dias
- Arquivo de logs críticos por 1 ano

#### Configuração
```yaml
logging:
  rotation:
    max_size: 100MB
    max_files: 10
    compress: true
  retention:
    days: 30
    critical_days: 365
```

## Tracing

### 1. Distributed Tracing

#### Spans
- Requisições HTTP
- Operações de banco
- Processamento de documentos
- Chamadas externas

#### Exemplo de Trace
```
Trace ID: abc123
├─ HTTP POST /api/v1/documents
│  ├─ Autenticação
│  ├─ Validação
│  └─ Upload para MinIO
└─ Processamento de Documento
   ├─ Download do arquivo
   ├─ Conversão para Markdown
   └─ Geração de embeddings
```

### 2. Integração com Jaeger

#### Configuração
```yaml
jaeger:
  enabled: true
  sampling:
    type: probabilistic
    param: 0.1
  storage:
    type: elasticsearch
    retention: 7d
```

## Alertas

### 1. Definição de Alertas

#### Critérios
- Erros HTTP > 1% por 5 minutos
- Latência p95 > 1s por 5 minutos
- CPU > 80% por 10 minutos
- Memória > 85% por 10 minutos
- Falhas de health check > 3

#### Exemplo de Regra
```yaml
groups:
- name: api
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Alta taxa de erros HTTP 5xx"
      description: "Taxa de erros acima de 1% nos últimos 5 minutos"
```

### 2. Notificações

#### Canais
- Email (todos os alertas)
- Slack (warning e critical)
- PagerDuty (apenas critical)
- SMS (apenas critical fora do horário)

#### Template de Notificação
```
[{{ .Status }}] {{ .AlertName }}
Severity: {{ .Severity }}
Description: {{ .Description }}
Value: {{ .Value }}
Time: {{ .StartsAt }}
```

## Dashboards

### 1. Grafana

#### Dashboards Principais
- Visão Geral da API
- Performance de Requisições
- Processamento de Documentos
- Saúde da Infraestrutura
- Erros e Exceções

#### Exemplo de Painel
```json
{
  "dashboard": {
    "title": "API Overview",
    "panels": [
      {
        "title": "Requisições por Minuto",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

### 2. Kibana

#### Visualizações
- Logs em Tempo Real
- Análise de Erros
- Padrões de Acesso
- Performance por Endpoint

## Health Checks

### 1. Endpoints

#### /health/live
- Verifica se a aplicação está rodando
- Resposta: 200 OK ou 503 Service Unavailable

#### /health/ready
- Verifica dependências (DB, Redis, etc)
- Resposta: 200 OK ou 503 Service Unavailable

#### /health/startup
- Verifica inicialização completa
- Resposta: 200 OK ou 503 Service Unavailable

### 2. Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Considerações de Implementação

### 1. Performance
- Coleta eficiente de métricas
- Agregação em tempo real
- Retenção otimizada
- Queries performáticas

### 2. Escalabilidade
- Distribuição de carga
- Cache de métricas
- Compressão de logs
- Indexação eficiente

### 3. Manutenção
- Documentação atualizada
- Backup de configurações
- Rotação automática
- Limpeza programada

### 4. Segurança
- Autenticação em todas as ferramentas
- Autorização baseada em roles
- Criptografia de dados
- Log de auditoria

## Próximos Passos

1. **Melhorias**
   - Implementar APM (Application Performance Monitoring)
   - Adicionar métricas de negócio
   - Melhorar visualizações
   - Otimizar alertas

2. **Integração**
   - Adicionar novos serviços
   - Unificar logs
   - Centralizar métricas
   - Automatizar dashboards

3. **Análise**
   - Implementar análise preditiva
   - Correlação de eventos
   - Detecção de anomalias
   - Insights automáticos

4. **Documentação**
   - Guias de uso das ferramentas
   - Runbooks de incidentes
   - Troubleshooting
   - Treinamento da equipe 