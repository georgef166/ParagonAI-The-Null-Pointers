# GenAI Agent Deployer (FastAPI + DigitalOcean Kubernetes)

This repo contains:
- **backend/**: A FastAPI orchestrator service exposing `/deploy` to create/update multiple GenAI agents on a Kubernetes cluster.
- **agent_runtime/**: A minimal FastAPI service that acts as a GenAI agent with a `/generate` endpoint. The backend deploys instances of this runtime.
- **k8s/**: Jinja2 templates for Kubernetes Deployment, Service, and optional Ingress/HPA.
- **scripts/**: Helper scripts to set kubeconfig from DigitalOcean and apply manifests.

## High-level flow

1. **User POSTs** to `/deploy` with one or more `agent.config.json` objects (either as a JSON list or multipart form files).
2. **backend/app/deployer.py** converts configs to K8s manifests using **Jinja2** templates.
3. **backend/app/do.py** applies manifests to your DigitalOcean Kubernetes cluster (via `kubectl`).
4. Each agent becomes reachable at an Ingress path: `/agents/<name>/generate` (configurable).

> You can also skip Ingress and use a `LoadBalancer` Service per agent if preferred.

---

## Quick start

### 0) Requirements

- Python 3.10+
- `kubectl`
- `doctl` (optional helper for kubeconfig)
- A DO Kubernetes cluster
- A container registry (DigitalOcean Container Registry or Docker Hub)

### 1) Build & push images

Set environment variables to simplify:

```bash
export REGISTRY="registry.hub.docker.com/<your-username>"   # or "registry.digitalocean.com/<your-registry>"
export IMAGE_TAG="v0.1.0"
```

**Build & push backend (orchestrator):**
```bash
cd backend
docker build -t "$REGISTRY/genai-deployer-backend:$IMAGE_TAG" .
docker push "$REGISTRY/genai-deployer-backend:$IMAGE_TAG"
```

**Build & push agent runtime:**
```bash
cd ../agent_runtime
docker build -t "$REGISTRY/genai-agent-runtime:$IMAGE_TAG" .
docker push "$REGISTRY/genai-agent-runtime:$IMAGE_TAG"
```

Update **backend/.env** (or environment) with your values, e.g.:
```
REGISTRY=registry.hub.docker.com/<your-username>
IMAGE_TAG=v0.1.0
KUBE_NAMESPACE=genai
INGRESS_CLASS=nginx
BASE_DOMAIN=your-domain.com
USE_INGRESS=true
OPENAI_API_KEY=sk-xxx                    # if using OpenAI in agent_runtime
```

### 2) Configure kubecontext

Use DigitalOcean to set kubeconfig (example):
```bash
./scripts/do_kubeconfig.sh <cluster-name>    # requires 'doctl' logged in
```

Or bring your own kubeconfig and set the context.

Create namespace (if it doesn’t exist):
```bash
kubectl create namespace genai
```

### 3) Run backend locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### 4) Deploy agents

#### Option A: JSON list
```bash
curl -X POST http://localhost:8080/deploy   -H "Content-Type: application/json"   -d '[
    {
      "name": "code-assistant",
      "template": "Code Assistant",
      "model": "OpenAI gpt-4o",
      "instruction": "You are a coding assistant. Provide correct, optimized code.",
      "resources": {"cpu": "500m", "memory": "512Mi"},
      "scaling": {"replicas": 1, "autoscale": false},
      "endpoints": ["generate"],
      "customEndpoints": [],
      "env": [],
      "logging": "info",
      "cloud": "None",
      "integrations": {}
    },
    {
      "name": "qa-assistant",
      "template": "Q&A",
      "model": "OpenAI gpt-4o-mini",
      "instruction": "Answer questions clearly and concisely.",
      "resources": {"cpu": "250m", "memory": "256Mi"},
      "scaling": {"replicas": 1, "autoscale": true, "minReplicas": 1, "maxReplicas": 3, "targetCPUUtilizationPercentage": 70},
      "endpoints": ["generate"],
      "env": [{"name": "TOPIC_DOMAIN", "value": "product-docs"}],
      "logging": "info"
    }
  ]'
```

#### Option B: Multipart form (upload multiple `agent.config.json` files)
```bash
curl -X POST http://localhost:8080/deploy   -F "files=@/path/agent1.config.json"   -F "files=@/path/agent2.config.json"
```

The backend returns a summary including generated manifest paths and apply results.

---

## Ingress vs Service

- **Ingress** (default): single domain + path: `https://{BASE_DOMAIN}/agents/<name>/generate`.
- **Service (LoadBalancer)**: set `USE_INGRESS=false` in `.env` to expose each agent via a DO LoadBalancer (incurs cost).

---

## Security notes

- Limit who can call `/deploy` (add auth) before using in production.
- Carefully manage API keys. Prefer referencing K8s Secrets and DO Secret Manager.
- RBAC service account for apply is recommended.
