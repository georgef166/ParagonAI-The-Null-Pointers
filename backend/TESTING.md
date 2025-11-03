# 🧪 Testing the Deployment System

## Prerequisites

✅ Backend server must be running first!

## Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd /Users/amanpurohit/code-playground/ParagonAI-The-Null-Pointers/backend
python3 -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Application startup complete.
```

**Keep this terminal open!** The server needs to stay running.

---

## Option 1: Use Interactive API Docs (Easiest - No Code!)

### Step A: Open Browser
```bash
open http://localhost:8000/docs
```

Or manually visit: **http://localhost:8000/docs**

### Step B: Try the Endpoints

1. **Check Health**
   - Click on `GET /health`
   - Click "Try it out"
   - Click "Execute"
   - You should see `"status": "healthy"`

2. **List Templates**
   - Click on `GET /templates`
   - Click "Try it out"
   - Click "Execute"
   - You'll see 6 available templates

3. **Deploy an Agent** (This will fail without DigitalOcean setup, but you can test the validation)
   - Click on `POST /deploy`
   - Click "Try it out"
   - Paste this JSON:
   ```json
   [
     {
       "name": "test-agent",
       "template": "Code Assistant",
       "model": "OpenAI gpt-4o",
       "instruction": "You are a test agent",
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
   ]
   ```
   - Click "Execute"

---

## Option 2: Use curl Commands

### Check Health
```bash
curl http://localhost:8000/health
```

### List Templates
```bash
curl http://localhost:8000/templates
```

### Deploy a Test Agent
```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "test-agent",
      "template": "Code Assistant",
      "model": "OpenAI gpt-4o",
      "instruction": "You are a test agent",
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

---

## Option 3: Use the Test Script

### In a NEW terminal (keep the server running!):

```bash
cd /Users/amanpurohit/code-playground/ParagonAI-The-Null-Pointers/backend
python3 test_deploy.py
```

This script will:
1. ✅ Check API health
2. ✅ List available templates
3. ✅ Deploy 3 test agents (code-assistant, data-analyst, customer-support)
4. ✅ Check deployment status
5. ✅ Optionally clean up

---

## Option 4: Use Python Requests

Create a test file:

```python
import requests
import json

# Deploy an agent
agent_config = {
    "name": "my-test-agent",
    "template": "Code Assistant",
    "model": "OpenAI gpt-4o",
    "instruction": "You are a test agent",
    "resources": {
        "cpu": "500m",
        "memory": "512Mi"
    },
    "scaling": {
        "replicas": 1,
        "autoscale": False
    },
    "endpoints": ["generate"],
    "customEndpoints": [],
    "env": [],
    "logging": "info",
    "cloud": "DigitalOcean",
    "integrations": {}
}

response = requests.post(
    "http://localhost:8000/deploy",
    json=[agent_config]
)

print(json.dumps(response.json(), indent=2))
```

---

## Expected Responses

### ✅ **Without DigitalOcean Setup** (Testing locally)

You'll get validation and build working, but push will fail:

```json
{
  "status": "failed",
  "message": "Deployed 0/1 agents successfully",
  "deployments": [
    {
      "agent_name": "test-agent",
      "status": "failed",
      "error": "Push failed: 401 Unauthorized"
    }
  ]
}
```

**This is expected!** It means:
- ✅ API is working
- ✅ Validation is working
- ✅ Docker build is working
- ❌ Need to authenticate with DigitalOcean (see FIX_AUTH_ERROR.md)

### ✅ **With DigitalOcean Setup** (Full deployment)

```json
{
  "status": "success",
  "message": "Deployed 1/1 agents successfully",
  "deployments": [
    {
      "agent_name": "test-agent",
      "status": "success",
      "image": "registry.digitalocean.com/genai-agents/test-agent:latest",
      "endpoints": ["https://YOUR-IP/test-agent"],
      "namespace": "default"
    }
  ]
}
```

---

## Quick Test Checklist

- [ ] Backend server running on port 8000
- [ ] Can access http://localhost:8000/docs in browser
- [ ] `GET /health` returns `"status": "healthy"`
- [ ] `GET /templates` shows 6 templates
- [ ] `POST /deploy` validates agent configuration
- [ ] Docker Desktop is running (for image builds)
- [ ] DigitalOcean authenticated (for actual deployments)

---

## Troubleshooting

### "Connection refused"
```bash
# Make sure server is running
cd /Users/amanpurohit/code-playground/ParagonAI-The-Null-Pointers/backend
python3 -m uvicorn main:app --reload --port 8000
```

### "401 Unauthorized"
This is normal without DigitalOcean setup. See `FIX_AUTH_ERROR.md` to fix.

### "Docker daemon not running"
```bash
# Start Docker Desktop
open -a Docker
```

### "Module not found"
```bash
# Install dependencies
cd backend
pip3 install -r requirements.txt
```

---

## What to Test

### 1. **API Validation** (No DigitalOcean needed)
- ✅ Health check works
- ✅ Templates list works
- ✅ Agent config validation works
- ✅ Error messages are clear

### 2. **Docker Build** (Docker Desktop needed)
- ✅ Docker images build successfully
- ✅ Correct base image used
- ✅ Dependencies installed

### 3. **Full Deployment** (DigitalOcean needed)
- ✅ Image pushes to registry
- ✅ Kubernetes manifests generated
- ✅ Resources deployed
- ✅ Agent accessible via endpoint

---

## Next Steps After Testing

1. **Local Testing** → Use Swagger UI at http://localhost:8000/docs
2. **Setup DigitalOcean** → Run `./setup_digitalocean.sh`
3. **Deploy Real Agents** → Use `python3 test_deploy.py`
4. **Access Agents** → Visit `http://LOAD_BALANCER_IP/agent-name/endpoint`

---

## Summary

**Quickest way to test right now:**

```bash
# Terminal 1: Start server
cd /Users/amanpurohit/code-playground/ParagonAI-The-Null-Pointers/backend
python3 -m uvicorn main:app --reload --port 8000

# Terminal 2: Open docs in browser
open http://localhost:8000/docs

# Or use curl
curl http://localhost:8000/health
curl http://localhost:8000/templates
```

That's it! The Swagger UI at `/docs` lets you test everything interactively. 🚀
