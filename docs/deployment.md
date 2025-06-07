# Guia de Deploy

Este guia fornece instruções detalhadas para implantação do sistema em diferentes ambientes.

## Ambientes

### Desenvolvimento (dev)
- Local
- Docker Compose
- Dados de teste

### Homologação (staging)
- Servidor dedicado
- Kubernetes
- Dados reais anonimizados

### Produção (prod)
- Cluster Kubernetes
- Alta disponibilidade
- Dados reais

## Pré-requisitos

### Infraestrutura
- Kubernetes 1.21+
- Helm 3.0+
- Docker 20.10+
- Nginx Ingress Controller
- Cert-Manager (SSL/TLS)

### Serviços
- MongoDB 5.0+
- PostgreSQL 13+ com pgvector
- MinIO
- RabbitMQ 3.9+
- Redis (cache)

### Monitoramento
- Prometheus
- Grafana
- ELK Stack
- Jaeger (tracing)

## Deploy com Docker Compose

### 1. Preparação

```bash
# Clone o repositório
git clone https://github.com/gwan/gwan-python-app.git
cd gwan-python-app

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env
```

### 2. Build e Deploy

```bash
# Build das imagens
docker-compose build

# Inicie os serviços
docker-compose up -d

# Verifique os logs
docker-compose logs -f
```

### 3. Verificação

```bash
# Status dos serviços
docker-compose ps

# Teste a API
curl http://localhost:8000/health

# Verifique os logs
docker-compose logs api
docker-compose logs worker
```

## Deploy com Kubernetes

### 1. Preparação do Cluster

```bash
# Crie o namespace
kubectl create namespace gwan

# Adicione o repositório Helm
helm repo add gwan https://gwan.github.io/helm-charts
helm repo update
```

### 2. Configuração

```bash
# Crie o arquivo de valores
cat > values.yaml << EOF
api:
  replicas: 3
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

worker:
  replicas: 2
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

mongodb:
  enabled: true
  auth:
    enabled: true
    rootPassword: ${MONGODB_ROOT_PASSWORD}
    database: gwan
    username: gwan
    password: ${MONGODB_PASSWORD}

postgresql:
  enabled: true
  auth:
    database: gwan_db
    username: gwan_user
    password: ${POSTGRES_PASSWORD}

minio:
  enabled: true
  auth:
    rootUser: minioadmin
    rootPassword: ${MINIO_ROOT_PASSWORD}

rabbitmq:
  enabled: true
  auth:
    username: gwan
    password: ${RABBITMQ_PASSWORD}
EOF
```

### 3. Deploy

```bash
# Instale o chart
helm upgrade --install gwan gwan/gwan-app \
  --namespace gwan \
  --values values.yaml \
  --wait

# Verifique o status
kubectl get all -n gwan
```

### 4. Configuração do Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gwan-ingress
  namespace: gwan
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.gwan.com.br
    secretName: gwan-tls
  rules:
  - host: api.gwan.com.br
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gwan-api
            port:
              number: 80
```

```bash
# Aplique o Ingress
kubectl apply -f ingress.yaml
```

## Monitoramento

### 1. Prometheus

```yaml
# prometheus-values.yaml
server:
  global:
    scrape_interval: 15s
  scrape_configs:
  - job_name: 'gwan-api'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      regex: gwan-api
      action: keep
  - job_name: 'gwan-worker'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      regex: gwan-worker
      action: keep
```

```bash
# Instale o Prometheus
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values prometheus-values.yaml
```

### 2. Grafana

```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gwan-dashboard
  namespace: monitoring
data:
  gwan-dashboard.json: |
    {
      "dashboard": {
        "id": null,
        "title": "Gwan Dashboard",
        "panels": [
          {
            "title": "API Requests",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "{{method}} {{path}}"
              }
            ]
          },
          {
            "title": "Worker Processing",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(worker_messages_processed_total[5m])",
                "legendFormat": "{{queue}}"
              }
            ]
          }
        ]
      }
    }
```

```bash
# Aplique o dashboard
kubectl apply -f grafana-dashboard.yaml
```

## Backup e Recuperação

### 1. MongoDB

```bash
# Backup
mongodump \
  --uri="mongodb://gwan:${MONGODB_PASSWORD}@mongodb:27017/gwan" \
  --out=/backup/$(date +%Y%m%d)

# Restore
mongorestore \
  --uri="mongodb://gwan:${MONGODB_PASSWORD}@mongodb:27017/gwan" \
  /backup/20240101
```

### 2. PostgreSQL

```bash
# Backup
pg_dump \
  -h postgresql \
  -U gwan_user \
  -d gwan_db \
  -F c \
  -f /backup/$(date +%Y%m%d).dump

# Restore
pg_restore \
  -h postgresql \
  -U gwan_user \
  -d gwan_db \
  /backup/20240101.dump
```

### 3. MinIO

```bash
# Backup
mc mirror \
  minio/documents \
  backup-minio/documents/$(date +%Y%m%d)

# Restore
mc mirror \
  backup-minio/documents/20240101 \
  minio/documents
```

## Escalabilidade

### 1. Auto-scaling

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gwan-api
  namespace: gwan
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gwan-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

```bash
# Aplique o HPA
kubectl apply -f hpa.yaml
```

### 2. Cache

```yaml
# redis-values.yaml
architecture: replication
auth:
  password: ${REDIS_PASSWORD}
master:
  persistence:
    enabled: true
    size: 10Gi
replica:
  replicaCount: 2
  persistence:
    enabled: true
    size: 10Gi
```

```bash
# Instale o Redis
helm upgrade --install redis bitnami/redis \
  --namespace gwan \
  --values redis-values.yaml
```

## Segurança

### 1. Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: gwan-api-policy
  namespace: gwan
spec:
  podSelector:
    matchLabels:
      app: gwan-api
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
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
```

```bash
# Aplique a Network Policy
kubectl apply -f network-policy.yaml
```

### 2. Secrets

```bash
# Crie os secrets
kubectl create secret generic gwan-secrets \
  --namespace gwan \
  --from-literal=mongodb-password=${MONGODB_PASSWORD} \
  --from-literal=postgres-password=${POSTGRES_PASSWORD} \
  --from-literal=rabbitmq-password=${RABBITMQ_PASSWORD} \
  --from-literal=minio-root-password=${MINIO_ROOT_PASSWORD} \
  --from-literal=redis-password=${REDIS_PASSWORD}
```

## Manutenção

### 1. Atualização

```bash
# Atualize a imagem
kubectl set image deployment/gwan-api \
  api=gwan/gwan-app:${NEW_VERSION} \
  -n gwan

# Verifique o rollout
kubectl rollout status deployment/gwan-api -n gwan
```

### 2. Rollback

```bash
# Liste os rollouts
kubectl rollout history deployment/gwan-api -n gwan

# Faça o rollback
kubectl rollout undo deployment/gwan-api \
  --to-revision=${REVISION} \
  -n gwan
```

### 3. Logs

```bash
# Logs da API
kubectl logs -l app=gwan-api -n gwan

# Logs do Worker
kubectl logs -l app=gwan-worker -n gwan

# Logs de todos os pods
kubectl logs -f --all-containers=true -l app=gwan-api -n gwan
```

## Troubleshooting

### 1. Verificação de Saúde

```bash
# Verifique os pods
kubectl get pods -n gwan

# Verifique os logs
kubectl logs -l app=gwan-api -n gwan

# Verifique os eventos
kubectl get events -n gwan
```

### 2. Problemas Comuns

1. **Pods em CrashLoopBackOff**
   - Verifique os logs
   - Verifique as configurações
   - Verifique os recursos

2. **Erro de Conexão**
   - Verifique as Network Policies
   - Verifique os Services
   - Verifique as credenciais

3. **Performance Degradada**
   - Verifique os recursos
   - Verifique os logs
   - Verifique as métricas

### 3. Recuperação

1. **Recuperação de Pod**
   ```bash
   # Delete o pod para recriação
   kubectl delete pod ${POD_NAME} -n gwan
   ```

2. **Recuperação de Deployment**
   ```bash
   # Faça rollback
   kubectl rollout undo deployment/gwan-api -n gwan
   ```

3. **Recuperação de Dados**
   ```bash
   # Restaure o backup mais recente
   ./scripts/restore.sh
   ``` 