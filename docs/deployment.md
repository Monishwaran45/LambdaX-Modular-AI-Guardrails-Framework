# Deployment Guide

## Deployment Options

LambdaX can be deployed in multiple ways depending on your needs:

1. **As a Python Library** - Embedded in your application
2. **As a Standalone API** - Microservice architecture
3. **As a Sidecar Container** - Kubernetes sidecar pattern

## 1. Library Deployment

### Installation

```bash
pip install lambdax
```

### Usage

```python
from lambdax import Orchestrator, PolicyEngine
from lambdax.guards import PromptInjectionGuard

policy_engine = PolicyEngine()
policy_engine.register_guard("prompt_injection", PromptInjectionGuard)
orchestrator = Orchestrator(policy_engine)

# Use in your application
result = await orchestrator.inspect_input(user_input, context)
```

### Pros
- Lowest latency (no network calls)
- Simple deployment
- Direct integration

### Cons
- Couples guardrails with application
- Harder to update independently
- Resource sharing with main app

## 2. Standalone API Deployment

### Docker

Build and run:

```bash
docker build -t lambdax:latest .
docker run -p 8000:8000 -v $(pwd)/policy.yaml:/app/policy.yaml lambdax:latest
```

### Docker Compose

```bash
docker-compose up -d
```

### Configuration

Environment variables:

```bash
LOG_LEVEL=INFO
CACHE_TTL=300
TIMEOUT=5.0
POLICY_PATH=/app/policy.yaml
```

### Health Checks

```bash
curl http://localhost:8000/health
```

### Metrics

Prometheus metrics available at:

```bash
curl http://localhost:8000/metrics
```

### Pros
- Independent scaling
- Language-agnostic clients
- Centralized policy management

### Cons
- Network latency
- Additional infrastructure
- More complex deployment

## 3. Kubernetes Deployment

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lambdax
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lambdax
  template:
    metadata:
      labels:
        app: lambdax
    spec:
      containers:
      - name: lambdax
        image: lambdax:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: policy
          mountPath: /app/policy.yaml
          subPath: policy.yaml
      volumes:
      - name: policy
        configMap:
          name: lambdax-policy
---
apiVersion: v1
kind: Service
metadata:
  name: lambdax
spec:
  selector:
    app: lambdax
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: lambdax-policy
data:
  policy.yaml: |
    version: 1
    policies:
      - id: default
        input_guards:
          - name: prompt_injection
            config:
              threshold: 0.8
```

### Sidecar Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest
        env:
        - name: LAMBDAX_URL
          value: "http://localhost:8000"
      - name: lambdax
        image: lambdax:latest
        ports:
        - containerPort: 8000
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lambdax-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lambdax
  minReplicas: 2
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

## Performance Tuning

### Model Optimization

1. **Use ONNX Runtime**:
```python
# Convert models to ONNX for faster inference
```

2. **Quantization**:
```python
# Use quantized models for lower latency
```

3. **Batch Processing**:
```python
# Process multiple requests in batches
```

### Caching Strategy

```python
# Adjust cache settings
orchestrator = Orchestrator(
    policy_engine,
    cache_ttl=600,      # 10 minutes
    cache_maxsize=5000  # 5000 entries
)
```

### Resource Allocation

Recommended resources per instance:

- **CPU**: 1-2 cores
- **Memory**: 2-4 GB (depends on models)
- **Disk**: 10 GB (for models)

## Monitoring

### Prometheus Metrics

Key metrics to monitor:

- `lambdax_guard_duration_seconds` - Guard execution time
- `lambdax_cache_hits_total` - Cache hit rate
- `lambdax_requests_total` - Total requests
- `lambdax_errors_total` - Error count

### Grafana Dashboard

Import the provided dashboard:

```bash
# Coming soon
```

### Logging

Configure structured logging:

```python
from lambdax.utils.logging import setup_logging

setup_logging(level="INFO", json_format=True)
```

## Security

### API Authentication

Add authentication middleware:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=403)
```

### TLS/SSL

Use reverse proxy (nginx, Traefik) for TLS termination.

### Network Policies

Restrict access in Kubernetes:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: lambdax-policy
spec:
  podSelector:
    matchLabels:
      app: lambdax
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: my-app
```

## Troubleshooting

### High Latency

1. Check guard execution times in logs
2. Verify cache hit rate
3. Consider model optimization
4. Scale horizontally

### Memory Issues

1. Reduce cache size
2. Use model quantization
3. Increase memory limits
4. Offload models to GPU

### Connection Errors

1. Check health endpoint
2. Verify network policies
3. Check resource limits
4. Review logs for errors

## Best Practices

1. **Always use health checks** in production
2. **Monitor cache hit rates** - aim for >80%
3. **Set appropriate timeouts** - balance latency vs accuracy
4. **Use horizontal scaling** - don't rely on vertical scaling
5. **Keep policies in version control**
6. **Test guard performance** before deploying
7. **Use structured logging** for better debugging
8. **Implement rate limiting** to prevent abuse
