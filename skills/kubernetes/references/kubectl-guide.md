# Kubernetes Essential Commands

## Cluster Info

```bash
# Get cluster info
kubectl cluster-info
kubectl get nodes
kubectl describe nodes

# Get API versions
kubectl api-versions
kubectl get api-resources
```

## Pods

```bash
# List pods
kubectl get pods
kubectl get pods -n kube-system
kubectl get pods -o wide

# Describe pod
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> -f  # Follow
kubectl logs <pod-name> -p  # Previous crashed instance

# Execute command
kubectl exec <pod-name> -- ls -la
kubectl exec -it <pod-name> -- /bin/bash
```

## Deployments

```bash
# Create deployment
kubectl create deployment nginx --image=nginx:latest

# Scale deployment
kubectl scale deployment/nginx --replicas=3

# Update deployment
kubectl set image deployment/nginx nginx=nginx:1.20

# Check rollout
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx
```

## Services

```bash
# Expose deployment
kubectl expose deployment/nginx --port=80 --type=LoadBalancer

# Get service
kubectl get svc
kubectl describe svc <service-name>

# Port forward
kubectl port-forward svc/nginx 8080:80
```

## ConfigMaps & Secrets

```bash
# Create ConfigMap
kubectl create configmap app-config --from-file=config.yaml

# Create Secret
kubectl create secret generic db-secret --from-literal=password=secret123

# View secrets
kubectl get secrets
kubectl get secret <secret-name> -o yaml
```

## Namespaces

```bash
# Create namespace
kubectl create namespace production

# Set default namespace
kubectl config set-context --current --namespace=production

# Get all resources
kubectl get all -n production
```

## Debugging

```bash
# Check events
kubectl get events

# Debug pod
kubectl debug <pod-name> -it --image=busybox

# Check resource usage
kubectl top pods
kubectl top nodes
```
