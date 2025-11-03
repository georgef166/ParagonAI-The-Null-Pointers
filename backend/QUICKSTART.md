# Quick Start: Deploy Agents to DigitalOcean

This is a **quick reference** for deploying GenAI agents to DigitalOcean Kubernetes.

## 📋 Prerequisites Checklist

- [ ] DigitalOcean account
- [ ] Docker Desktop installed and running
- [ ] `doctl` CLI installed (`brew install doctl`)
- [ ] `kubectl` installed (`brew install kubectl`)
- [ ] OpenAI API key
- [ ] DigitalOcean API token

## 🚀 Quick Setup (5 Minutes)

### 1. Authenticate DigitalOcean CLI
```bash
doctl auth init
# Paste your DigitalOcean API token when prompted
```

### 2. Create Kubernetes Cluster
```bash
# Create cluster (takes 5-10 minutes)
doctl kubernetes cluster create genai-agents-cluster \
  --region nyc1 \
  --version latest \
  --size s-2vcpu-4gb \
  --count 2

# Configure kubectl
doctl kubernetes cluster kubeconfig save genai-agents-cluster

# Verify connection
kubectl cluster-info
```

### 3. Create Container Registry
```bash
# Create registry
doctl registry create genai-agents

# Login
doctl registry login
```

### 4. Create OpenAI Secret
```bash
kubectl create secret generic openai-credentials \
  --from-literal=api-key=YOUR_OPENAI_API_KEY
```

### 5. Install NGINX Ingress
```bash
# Install
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# Wait for load balancer (2-3 minutes)
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Get external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### 6. Configure Backend
Edit `backend/.env`:
```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
DO_API_TOKEN=dop_v1_your-do-token

# Get load balancer IP from step 5
DOMAIN=1.2.3.4  # Replace with actual IP

# Registry
DOCKER_REGISTRY=registry.digitalocean.com
DOCKER_REGISTRY_NAMESPACE=genai-agents
```

### 7. Start Backend
```bash
cd backend
./venv/bin/python -m uvicorn main:app --reload --port 8000
```

## 🎯 Deploy Your First Agent

### Example Configuration
```json
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
```

### Deploy via API
```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "code-assistant",
      "template": "Code Assistant",
      "model": "OpenAI gpt-4o",
      "instruction": "You are a coding assistant.",
      "resources": {"cpu": "500m", "memory": "512Mi"},
      "scaling": {"replicas": 1, "autoscale": false},
      "endpoints": ["generate"],
      "customEndpoints": [],
      "env": [],
      "logging": "info",
      "cloud": "DigitalOcean",
      "integrations": {}
    }
  ]'
```

### Or Use Test Script
```bash
cd backend
python test_deploy.py
```

## 📊 Manage Deployments

### List All Agents
```bash
curl http://localhost:8000/deployments
```

### Get Agent Status
```bash
curl http://localhost:8000/deployments/code-assistant
```

### Delete Agent
```bash
curl -X DELETE http://localhost:8000/deployments/code-assistant
```

### View Kubernetes Resources
```bash
# Pods
kubectl get pods

# Deployments
kubectl get deployments

# Services
kubectl get services

# Ingress
kubectl get ingress

# Logs
kubectl logs -l app=code-assistant --tail=50 -f
```

## 🔗 Access Your Agent

Once deployed, agents are accessible at:
```
http://LOAD_BALANCER_IP/AGENT_NAME/ENDPOINT
```

Example:
```bash
curl -X POST http://1.2.3.4/code-assistant/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to sort a list",
    "max_tokens": 500
  }'
```

## 📚 Available Templates

1. **Code Assistant** - Help with coding tasks
2. **Data Analyst** - Analyze data and create visualizations
3. **Customer Support** - Customer service interactions
4. **Content Writer** - Generate content and copy
5. **Research Assistant** - Research and summarization
6. **General Assistant** - General purpose tasks

## 🎛️ Configuration Options

### Resources
- `cpu`: "500m", "1", "2" (millicores or cores)
- `memory`: "512Mi", "1Gi", "2Gi"

### Scaling
```json
{
  "replicas": 2,
  "autoscale": true,
  "min_replicas": 1,
  "max_replicas": 10,
  "target_cpu_percentage": 70
}
```

### Environment Variables
```json
{
  "env": [
    {"name": "API_KEY", "value": "xyz"},
    {"name": "DEBUG", "value": "true"}
  ]
}
```

### Logging Levels
- `debug` - Verbose logging
- `info` - Standard logging
- `warning` - Warnings only
- `error` - Errors only

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Start backend
cd backend
./venv/bin/python -m uvicorn main:app --reload --port 8000
```

### Docker build fails
```bash
# Make sure Docker Desktop is running
open -a Docker

# Wait for Docker to start, then retry
```

### Kubectl connection fails
```bash
# Re-download kubeconfig
doctl kubernetes cluster kubeconfig save genai-agents-cluster

# Verify
kubectl cluster-info
```

### Registry push fails
```bash
# Re-authenticate
doctl registry login

# Verify registry
doctl registry get
```

### Pod not starting
```bash
# Check pod status
kubectl get pods

# View logs
kubectl logs POD_NAME

# Describe pod
kubectl describe pod POD_NAME

# Common issues:
# 1. OpenAI secret not created
kubectl get secret openai-credentials

# 2. Image pull errors - check registry login
doctl registry login

# 3. Resource constraints - check node resources
kubectl describe nodes
```

## 💰 Cost Estimate

**Minimum Setup:**
- Kubernetes Cluster: 2 nodes @ $24/month each = **$48/month**
- Container Registry: **$5/month** (150 GB storage)
- Load Balancer: **$12/month**

**Total: ~$65/month**

Scale up/down based on usage!

## 🔧 Production Checklist

- [ ] Configure custom domain with DNS
- [ ] Set up SSL/TLS certificates (cert-manager)
- [ ] Enable autoscaling for agents
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backup strategy
- [ ] Implement authentication/authorization
- [ ] Set up rate limiting
- [ ] Configure log aggregation
- [ ] Set up alerting
- [ ] Document runbooks

## 📖 Additional Resources

- [Full Setup Guide](./SETUP_GUIDE.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [Example Configurations](./examples/)

## 🆘 Need Help?

1. Check the logs: `kubectl logs -l app=AGENT_NAME`
2. Review the setup guide: `SETUP_GUIDE.md`
3. Test the API: `http://localhost:8000/docs`
4. Run test script: `python test_deploy.py`
