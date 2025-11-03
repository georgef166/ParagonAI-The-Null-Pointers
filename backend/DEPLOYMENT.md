# GenAI Agent Deployment - Deployment Guide

This guide will walk you through deploying the GenAI Agent Deployment system to DigitalOcean Kubernetes.

## Prerequisites

1. **DigitalOcean Account**
   - Active DigitalOcean account
   - Container Registry created
   - Kubernetes cluster running (1.28+)

2. **Local Tools**
   - Docker Desktop installed and running
   - kubectl installed and configured
   - doctl (DigitalOcean CLI) installed
   - Python 3.11+

3. **API Keys**
   - OpenAI API key
   - DigitalOcean API token

## Step-by-Step Deployment

### 1. Setup DigitalOcean

```bash
# Login to DigitalOcean
doctl auth init

# Create a Kubernetes cluster (if not exists)
doctl kubernetes cluster create genai-agents-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"

# Download kubeconfig
doctl kubernetes cluster kubeconfig save genai-agents-cluster

# Verify connection
kubectl cluster-info
```

### 2. Setup Container Registry

```bash
# Create registry (if not exists)
doctl registry create genai-agents

# Login to registry
doctl registry login

# Get registry endpoint
doctl registry get
```

### 3. Install Required Cluster Components

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/do/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s
```

### 4. Configure DNS

1. Get LoadBalancer IP:
```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

2. Create A records in your DNS:
   - `api.genai-agents.example.com` → LoadBalancer IP
   - `*.genai-agents.example.com` → LoadBalancer IP

### 5. Setup SSL Certificate Issuer

```bash
# Create Let's Encrypt issuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 6. Deploy Backend

```bash
cd backend

# Copy and configure environment
cp .env.example .env
nano .env  # Update with your credentials

# Run setup script
chmod +x setup.sh deploy.sh
./setup.sh

# Deploy to Kubernetes
./deploy.sh
```

### 7. Verify Deployment

```bash
# Check pods
kubectl get pods -n genai-agents

# Check services
kubectl get svc -n genai-agents

# Check ingress
kubectl get ingress -n genai-agents

# View logs
kubectl logs -f deployment/genai-deployment-backend -n genai-agents
```

### 8. Test the API

```bash
# Test health endpoint
curl https://api.genai-agents.example.com/health

# List templates
curl https://api.genai-agents.example.com/templates

# Deploy a test agent
curl -X POST https://api.genai-agents.example.com/deploy \
  -H "Content-Type: application/json" \
  -d @examples/single_agent.json
```

## Using the Deployment System

### Deploy Agents via API

```bash
# Single agent
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @examples/single_agent.json

# Multiple agents
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @examples/deploy_multiple_agents.json
```

### Deploy Agents via Python Script

```bash
# List available templates
python examples/example_deploy.py templates

# Deploy from config
python examples/example_deploy.py deploy examples/single_agent.json

# List deployments
python examples/example_deploy.py list

# Get deployment status
python examples/example_deploy.py status research-assistant

# Delete deployment
python examples/example_deploy.py delete research-assistant
```

### Access Deployed Agents

Once deployed, agents are accessible at:
```
https://genai-agents.example.com/{agent-name}/
```

Example endpoints:
```bash
# Health check
curl https://genai-agents.example.com/code-assistant/health

# Generate endpoint
curl -X POST https://genai-agents.example.com/code-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate factorial",
    "max_tokens": 500
  }'
```

## Monitoring & Management

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/genai-deployment-backend -n genai-agents

# Specific agent logs
kubectl logs -f deployment/code-assistant -n genai-agents
```

### Scale Deployments

```bash
# Manual scaling
kubectl scale deployment code-assistant -n genai-agents --replicas=3

# Or update via API with autoscaling configuration
```

### Delete Agents

```bash
# Via API
curl -X DELETE http://localhost:8000/deployments/code-assistant

# Via kubectl
kubectl delete deployment code-assistant -n genai-agents
kubectl delete service code-assistant -n genai-agents
kubectl delete ingress code-assistant -n genai-agents
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n genai-agents

# Check events
kubectl get events -n genai-agents --sort-by='.lastTimestamp'

# Check resource availability
kubectl top nodes
kubectl top pods -n genai-agents
```

### Image Pull Errors

```bash
# Verify registry credentials
doctl registry login

# Check if image exists
doctl registry repository list-v2

# Manually pull image
docker pull registry.digitalocean.com/genai-agents/deployment-backend:latest
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress -n genai-agents

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check certificate
kubectl get certificate -n genai-agents
kubectl describe certificate deployment-backend-tls -n genai-agents
```

### Agent Not Responding

```bash
# Check agent pod logs
kubectl logs deployment/code-assistant -n genai-agents

# Check if OpenAI key is configured
kubectl get secret openai-credentials -n genai-agents -o yaml

# Test direct pod access
kubectl port-forward deployment/code-assistant 8080:8080 -n genai-agents
curl http://localhost:8080/health
```

## Scaling Considerations

### Resource Limits

Default resources per agent:
- CPU: 500m (0.5 cores)
- Memory: 512Mi

Adjust based on your needs:
```json
{
  "resources": {
    "cpu": "1000m",
    "memory": "1Gi"
  }
}
```

### Autoscaling

Enable HPA for automatic scaling:
```json
{
  "scaling": {
    "replicas": 2,
    "autoscale": true,
    "min_replicas": 2,
    "max_replicas": 10,
    "target_cpu_percentage": 70
  }
}
```

### Cluster Sizing

Recommended cluster configuration:
- **Development**: 2 nodes × 2vCPU/4GB RAM
- **Production**: 3+ nodes × 4vCPU/8GB RAM
- **High Traffic**: 5+ nodes × 8vCPU/16GB RAM

## Cost Optimization

1. **Use autoscaling** to scale down during low traffic
2. **Set resource limits** appropriately
3. **Delete unused deployments**
4. **Use spot instances** for non-production (when available)
5. **Monitor usage** with DigitalOcean dashboard

## Security Best Practices

1. **Never commit secrets** - use Kubernetes secrets
2. **Enable RBAC** - limit service account permissions
3. **Use TLS** - ensure all traffic is encrypted
4. **Rotate API keys** - regularly update credentials
5. **Network policies** - restrict pod-to-pod communication
6. **Image scanning** - scan Docker images for vulnerabilities

## Backup & Disaster Recovery

```bash
# Backup Kubernetes manifests
kubectl get all -n genai-agents -o yaml > backup.yaml

# Backup secrets (encrypted)
kubectl get secrets -n genai-agents -o yaml > secrets.yaml

# Store backups securely (don't commit secrets to git!)
```

## Next Steps

1. Setup monitoring with Prometheus/Grafana
2. Configure centralized logging
3. Implement CI/CD pipeline
4. Add authentication/authorization
5. Setup rate limiting
6. Configure cost alerts

## Support

For issues or questions:
1. Check logs: `kubectl logs -n genai-agents`
2. Review documentation
3. Check DigitalOcean status page
4. Contact support

## Additional Resources

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
