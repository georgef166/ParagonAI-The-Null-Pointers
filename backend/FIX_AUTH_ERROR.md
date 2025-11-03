# Fix: 401 Unauthorized - Docker Registry Authentication

## ❌ **The Problem**

```
Push failed: failed to authorize: 401 Unauthorized
```

This means Docker cannot push to DigitalOcean Container Registry because it's not authenticated.

## ✅ **Quick Fix (3 Steps)**

### **Step 1: Install DigitalOcean CLI**

```bash
# macOS
brew install doctl

# Or download from:
# https://docs.digitalocean.com/reference/doctl/how-to/install/
```

### **Step 2: Authenticate & Create Registry**

```bash
# Login to DigitalOcean
doctl auth init
# When prompted, paste your API token from:
# https://cloud.digitalocean.com/account/api/tokens

# Create container registry (if you haven't)
doctl registry create genai-agents

# Login Docker to DigitalOcean registry
doctl registry login
```

### **Step 3: Try Deploying Again**

```bash
cd backend
python test_deploy.py
```

## 🚀 **Full Setup (Run Once)**

We've created an automated setup script:

```bash
cd backend
./setup_digitalocean.sh
```

This script will:
- ✅ Check if `doctl` is installed
- ✅ Authenticate with DigitalOcean
- ✅ Create container registry
- ✅ Login Docker to registry
- ✅ Optionally create Kubernetes cluster
- ✅ Install NGINX Ingress Controller
- ✅ Create OpenAI API secret
- ✅ Update your `.env` file

## 📋 **Manual Setup (Alternative)**

### 1. Install Tools
```bash
# Install doctl
brew install doctl

# Install kubectl (for Kubernetes)
brew install kubectl
```

### 2. Authenticate DigitalOcean
```bash
# Get API token from: https://cloud.digitalocean.com/account/api/tokens
doctl auth init
```

### 3. Create & Configure Registry
```bash
# Create registry
doctl registry create genai-agents

# Verify registry exists
doctl registry get

# Login Docker
doctl registry login
```

### 4. Create Kubernetes Cluster (Optional)
```bash
# Create cluster
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

### 5. Create OpenAI Secret
```bash
# Replace with your actual OpenAI API key
kubectl create secret generic openai-credentials \
  --from-literal=api-key=sk-your-openai-api-key-here
```

### 6. Install NGINX Ingress
```bash
# Install Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Get Load Balancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### 7. Update .env File
```bash
# Edit backend/.env
OPENAI_API_KEY=sk-your-openai-key
DO_API_TOKEN=dop_v1_your-do-token
DOMAIN=YOUR_LOAD_BALANCER_IP  # From step 6
DOCKER_REGISTRY=registry.digitalocean.com
DOCKER_REGISTRY_NAMESPACE=genai-agents
```

## 🧪 **Test Deployment**

```bash
cd backend

# Start backend
./venv/bin/python -m uvicorn main:app --reload --port 8000

# In another terminal, deploy test agent
python test_deploy.py
```

## ✅ **Expected Success Output**

```
🚀 Deploying 1 agent(s)...
✅ Status: success
📝 Message: Deployed 1/1 agents successfully

  Agent: code-assistant
  Status: success
  Image: registry.digitalocean.com/genai-agents/code-assistant:latest
  Endpoints: https://YOUR-IP/code-assistant
```

## 🔍 **Verify Deployment**

```bash
# Check Docker can push
docker images | grep genai-agents

# Check Kubernetes deployment
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress
```

## 🆘 **Troubleshooting**

### "doctl: command not found"
```bash
brew install doctl
```

### "Docker daemon not running"
```bash
# Start Docker Desktop
open -a Docker

# Wait for it to start, then retry
```

### "Registry not found"
```bash
# Create registry
doctl registry create genai-agents

# Verify
doctl registry get
```

### "Authentication failed"
```bash
# Re-authenticate Docker
doctl registry login

# Verify Docker config
cat ~/.docker/config.json | grep digitalocean
```

### "kubectl connection refused"
```bash
# Re-download kubeconfig
doctl kubernetes cluster kubeconfig save genai-agents-cluster

# Verify
kubectl cluster-info
```

## 📚 **More Help**

- Run automated setup: `./setup_digitalocean.sh`
- Quick start guide: `QUICKSTART.md`
- Full documentation: `SETUP_GUIDE.md`
- API documentation: http://localhost:8000/docs

## 💡 **Summary**

The key command you need right now:

```bash
# This authenticates Docker with DigitalOcean registry
doctl registry login
```

After running this, your deployment should work! 🚀
