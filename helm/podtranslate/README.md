# PodTranslate Helm Chart

Official Helm chart for deploying PodTranslate on Kubernetes.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure (for persistence)
- GPU nodes (for audio processing with Whisper)

## Installing the Chart

### Add the repository

```bash
helm repo add podtranslate https://charts.podtranslate.com
helm repo update
```

### Install with default configuration

```bash
helm install my-podtranslate podtranslate/podtranslate
```

### Install with custom values

```bash
helm install my-podtranslate podtranslate/podtranslate -f custom-values.yaml
```

### Install from local chart

```bash
cd helm
helm install my-podtranslate ./podtranslate
```

## Uninstalling the Chart

```bash
helm uninstall my-podtranslate
```

## Configuration

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imageRegistry` | Global Docker image registry | `""` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |

### API Gateway Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `apiGateway.enabled` | Enable API Gateway | `true` |
| `apiGateway.replicaCount` | Number of replicas | `3` |
| `apiGateway.image.repository` | Image repository | `podtranslate/api-gateway` |
| `apiGateway.image.tag` | Image tag | `latest` |
| `apiGateway.service.port` | Service port | `3000` |
| `apiGateway.resources.requests.memory` | Memory request | `256Mi` |
| `apiGateway.resources.requests.cpu` | CPU request | `250m` |
| `apiGateway.autoscaling.enabled` | Enable HPA | `true` |
| `apiGateway.autoscaling.minReplicas` | Minimum replicas | `3` |
| `apiGateway.autoscaling.maxReplicas` | Maximum replicas | `10` |

### Audio Processing Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `audioProcessing.enabled` | Enable Audio Processing | `true` |
| `audioProcessing.replicaCount` | Number of replicas | `2` |
| `audioProcessing.resources.requests.nvidia.com/gpu` | GPU request | `1` |
| `audioProcessing.env.WHISPER_MODEL` | Whisper model size | `large-v3` |
| `audioProcessing.persistence.enabled` | Enable model cache persistence | `true` |
| `audioProcessing.persistence.size` | PVC size | `50Gi` |
| `audioProcessing.nodeSelector` | Node selector for GPU nodes | `{workload: gpu}` |

### Distribution Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `distribution.enabled` | Enable Distribution Service | `true` |
| `distribution.replicaCount` | Number of replicas | `2` |
| `distribution.resources.requests.memory` | Memory request | `512Mi` |

### Analytics Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `analytics.enabled` | Enable Analytics Service | `true` |
| `analytics.replicaCount` | Number of replicas | `2` |

### AI Tools Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `aiTools.enabled` | Enable AI Tools Service | `true` |
| `aiTools.replicaCount` | Number of replicas | `2` |

### Dashboard Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `dashboard.enabled` | Enable Dashboard | `true` |
| `dashboard.replicaCount` | Number of replicas | `2` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable Ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts[0].host` | Hostname | `podtranslate.example.com` |
| `ingress.tls[0].secretName` | TLS secret name | `podtranslate-tls` |

### PostgreSQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL | `true` |
| `postgresql.auth.username` | PostgreSQL username | `podtranslate` |
| `postgresql.auth.password` | PostgreSQL password | `changeme` |
| `postgresql.auth.database` | PostgreSQL database | `podtranslate` |
| `postgresql.primary.persistence.size` | PVC size | `20Gi` |

### Redis Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis | `true` |
| `redis.auth.password` | Redis password | `changeme` |
| `redis.master.persistence.size` | PVC size | `8Gi` |

### RabbitMQ Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `rabbitmq.enabled` | Enable RabbitMQ | `true` |
| `rabbitmq.auth.username` | RabbitMQ username | `podtranslate` |
| `rabbitmq.auth.password` | RabbitMQ password | `changeme` |
| `rabbitmq.persistence.size` | PVC size | `10Gi` |

### Secrets

Configure API keys and credentials:

```yaml
secrets:
  openai:
    apiKey: "sk-..."
  deepl:
    apiKey: "..."
  spotify:
    clientId: "..."
    clientSecret: "..."
  apple:
    teamId: "..."
    keyId: "..."
    privateKey: "..."
  google:
    clientId: "..."
    clientSecret: "..."
  aws:
    accessKeyId: "..."
    secretAccessKey: "..."
```

## Example Configurations

### Minimal Installation (Development)

```yaml
# values-dev.yaml
apiGateway:
  replicaCount: 1
  autoscaling:
    enabled: false

audioProcessing:
  replicaCount: 1
  autoscaling:
    enabled: false
  resources:
    requests:
      nvidia.com/gpu: 0  # No GPU

postgresql:
  primary:
    persistence:
      size: 5Gi

redis:
  master:
    persistence:
      size: 1Gi
```

```bash
helm install my-podtranslate ./podtranslate -f values-dev.yaml
```

### Production Installation

```yaml
# values-prod.yaml
global:
  imageRegistry: my-registry.com

ingress:
  enabled: true
  hosts:
    - host: podtranslate.mycompany.com
      paths:
        - path: /api
          pathType: Prefix
          service: api-gateway
        - path: /
          pathType: Prefix
          service: dashboard
  tls:
    - secretName: podtranslate-tls
      hosts:
        - podtranslate.mycompany.com

secrets:
  openai:
    apiKey: "sk-prod-..."
  aws:
    accessKeyId: "AKIA..."
    secretAccessKey: "..."

postgresql:
  primary:
    persistence:
      storageClass: fast-ssd
      size: 100Gi

audioProcessing:
  replicaCount: 5
  autoscaling:
    maxReplicas: 20
```

```bash
helm install my-podtranslate ./podtranslate -f values-prod.yaml
```

### Using External Databases

```yaml
# values-external-db.yaml
postgresql:
  enabled: false
  external:
    host: postgres.example.com
    port: 5432
    database: podtranslate
    username: podtranslate
    password: "secure-password"

redis:
  enabled: false
  external:
    host: redis.example.com
    port: 6379
    password: "secure-password"

rabbitmq:
  enabled: false
  external:
    host: rabbitmq.example.com
    port: 5672
    username: podtranslate
    password: "secure-password"
```

## Upgrade

```bash
helm upgrade my-podtranslate podtranslate/podtranslate -f custom-values.yaml
```

## Monitoring

The chart includes ServiceMonitor resources for Prometheus:

```yaml
serviceMonitor:
  enabled: true
  interval: 30s
```

## Persistence

The following components use persistent volumes:

- **PostgreSQL**: Stores application data
- **Redis**: Stores cache and rate limiting data
- **RabbitMQ**: Stores message queue data
- **Audio Processing**: Stores Whisper model cache

## GPU Support

Audio processing requires NVIDIA GPUs. Ensure:

1. GPU nodes are available in your cluster
2. NVIDIA device plugin is installed
3. Node selector is configured:

```yaml
audioProcessing:
  nodeSelector:
    workload: gpu
```

## Troubleshooting

### Check pod status

```bash
kubectl get pods -l app.kubernetes.io/instance=my-podtranslate
```

### View logs

```bash
kubectl logs -l app.kubernetes.io/component=api-gateway -f
```

### Check HPA status

```bash
kubectl get hpa
```

### Test API

```bash
kubectl port-forward svc/my-podtranslate-api-gateway 3000:3000
curl http://localhost:3000/api/v1/health
```

## Support

- Documentation: https://docs.podtranslate.com
- Issues: https://github.com/podtranslate/podtranslate/issues

## License

MIT
