# Kubernetes Concepts

## Pod Lifecycle

```
Pending → Running → Succeeded (or Failed)
```

- **Pending** - Waiting for resources
- **Running** - Container is executing
- **Succeeded** - Completed successfully (Job/Pod)
- **Failed** - Error occurred
- **Unknown** - Can't determine status

## Resource Requests & Limits

```yaml
resources:
  requests:
    cpu: "100m"      # Minimum needed
    memory: "128Mi"
  limits:
    cpu: "500m"      # Maximum allowed
    memory: "512Mi"
```

## labels vs Annotations

**Labels**: Used for selection and grouping
```yaml
labels:
  app: myapp
  version: v1.0.0
```

**Annotations**: Metadata and configuration
```yaml
annotations:
  description: "My application"
  build.timestamp: "2024-01-20"
```

## ReplicaSet vs Deployment

**ReplicaSet**: Ensures number of replicas
**Deployment**: Manages ReplicaSets, provides rolling updates

```yaml
kind: Deployment  # Use this
```

## Selectors

```yaml
selector:
  matchLabels:
    app: myapp
    
# Matches pods with both labels set
```

## Init Containers

Run before main container:

```yaml
initContainers:
- name: wait-for-db
  image: busybox
  command: ['sh', '-c', 'until nslookup db; do sleep 1; done']
```

## Health Checks

```yaml
livenessProbe:           # Is container alive?
  httpGet:
    path: /health
    port: 8080
    
readinessProbe:          # Ready to receive traffic?
  httpGet:
    path: /ready
    port: 8080
```
