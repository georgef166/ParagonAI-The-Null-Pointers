# DigitalOcean Setup Guide

This guide will help you deploy GenAI agents to DigitalOcean Kubernetes.

## Prerequisites

1. DigitalOcean account
2. `doctl` CLI installed
3. `kubectl` installed
4. Docker Desktop running
5. OpenAI API key

## Step 1: Install Required Tools

### Install doctl (DigitalOcean CLI)
```bash
# macOS
brew install doctl

# Authenticate
doctl auth init
```

### Install kubectl
```bash
# macOS
brew install kubectl
```

## Step 2: Create DigitalOcean Kubernetes Cluster

### Option A: Using Web Console
1. Go to https://cloud.digitalocean.com/kubernetes/clusters
2. Click "Create Kubernetes Cluster"
3. Choose:
   - Name: `genai-agents-cluster`
   - Region: Select closest to you
   - Node pool: Basic nodes, 2 vCPU, 4 GB RAM, 2 nodes
4. Click "Create Cluster"
5. Wait 5-10 minutes for cluster creation

### Option B: Using doctl CLI
```bash
# Create cluster
doctl kubernetes cluster create genai-agents-cluster \
  --region nyc1 \
  --version latest \
  --size s-2vcpu-4gb \
  --count 2

# Configure kubectl
doctl kubernetes cluster kubeconfig save genai-agents-cluster
```

## Step 3: Create Container Registry

```bash
# Create registry (one-time)
doctl registry create genai-agents

# Get registry name
doctl registry get

# Login to registry
doctl registry login
```

## Step 4: Create OpenAI API Key Secret

```bash
# Create Kubernetes secret for OpenAI API key
kubectl create secret generic openai-credentials \
  --from-literal=api-key=YOUR_OPENAI_API_KEY_HERE
```

## Step 5: Install NGINX Ingress Controller

```bash
# Install NGINX ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# Wait for load balancer
kubectl get svc -n ingress-nginx

# Get external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Step 6: Configure DNS (Optional)

1. Get the Load Balancer IP from Step 5
2. Create an A record pointing `*.genai-agents.yourdomain.com` to the IP
3. Or use the IP directly in requests

## Step 7: Configure Backend Environment

Edit `.env` file:

```bash
# DigitalOcean API Token
# Get from: https://cloud.digitalocean.com/account/api/tokens
DO_API_TOKEN=dop_v1_xxxxxxxxxxxxxxxxxxxxx

# OpenAI API Key
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Domain (use load balancer IP if no domain)
DOMAIN=1.2.3.4  # or genai-agents.yourdomain.com

# Registry namespace
DOCKER_REGISTRY_NAMESPACE=genai-agents
```

## Step 8: Start the Backend

```bash
cd backend
./venv/bin/python -m uvicorn main:app --reload --port 8000
```

## Step 9: Deploy Your First Agent

### Using curl
```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "code-assistant",
      "template": "Code Assistant",
      "model": "OpenAI gpt-4o",
      "instruction": "You are a coding assistant. Provide correct, optimized code.",
      "resources": {
        "cpu": "500m",
        "memory": "512Mi"
      },
      "scaling": {
        "replicas": 1,
        "autoscale": false
      },
      "endpoints": ["generate"],
      "customEndpoints": [],
      "env": [],
      "logging": "info",
      "cloud": "DigitalOcean",
      "integrations": {}
    }
  ]'
```

### Using Python Client
```bash
cd examples
python example_deploy.py deploy single_agent.json
```

## Step 10: Access Your Agent

Once deployed, your agent will be available at:

```
https://DOMAIN/code-assistant/generate
# or
http://LOAD_BALANCER_IP/code-assistant/generate
```

Example request:
```bash
curl -X POST https://your-domain/code-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "max_tokens": 500
  }'
```

## Management Commands

### List all deployments
```bash
curl http://localhost:8000/deployments
```

### Get deployment status
```bash
curl http://localhost:8000/deployments/code-assistant
```

### Delete deployment
```bash
curl -X DELETE http://localhost:8000/deployments/code-assistant
```

### View Kubernetes resources
```bash
# View all pods
kubectl get pods

# View deployments
kubectl get deployments

# View services
kubectl get services

# View ingress
kubectl get ingress

# View logs
kubectl logs -l app=code-assistant

# Get pod details
kubectl describe pod <pod-name>
```

## Troubleshooting

### Docker Build Fails
- Ensure Docker Desktop is running
- Check Docker has enough resources (4GB+ RAM)

### Kubectl Connection Fails
```bash
# Verify cluster connection
kubectl cluster-info

# Re-download kubeconfig
doctl kubernetes cluster kubeconfig save genai-agents-cluster
```

### Registry Push Fails
```bash
# Re-authenticate with registry
doctl registry login

# Check registry exists
doctl registry get
```

### Agent Not Accessible
```bash
# Check ingress controller
kubectl get svc -n ingress-nginx

# Check pod status
kubectl get pods

# View pod logs
kubectl logs -l app=code-assistant

# Check ingress rules
kubectl get ingress code-assistant -o yaml
```

### OpenAI API Errors
```bash
# Verify secret exists
kubectl get secret openai-credentials

# Update secret if needed
kubectl delete secret openai-credentials
kubectl create secret generic openai-credentials --from-literal=api-key=NEW_KEY
```

## Cost Optimization

1. **Node Sizing**: Start with smaller nodes (s-2vcpu-4gb) and scale up
2. **Autoscaling**: Enable HPA for variable load
3. **Resource Limits**: Set appropriate CPU/memory limits
4. **Registry**: Clean up old images regularly

```bash
# Delete old registry images
doctl registry garbage-collection start genai-agents --include-untagged-manifests
```

## Next Steps

1. Set up SSL/TLS certificates with cert-manager
2. Add monitoring with Prometheus/Grafana
3. Implement authentication/authorization
4. Add rate limiting
5. Set up CI/CD pipeline
6. Configure backup strategy

## Resources

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [Container Registry Guide](https://docs.digitalocean.com/products/container-registry/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
