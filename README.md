# ParagonAI - GenAI Agent Deployment Platform

A comprehensive platform for deploying and managing GenAI agents on DigitalOcean Kubernetes clusters.

## 🚀 Project Overview

This project provides a complete FastAPI-based backend system that automates the deployment of GenAI agents to Kubernetes. It accepts agent configurations via REST API, automatically builds Docker containers, and deploys them as scalable services with SSL endpoints.

## 📁 Project Structure

```
ParagonAI-The-Null-Pointers/
├── backend/              # FastAPI deployment backend ⭐ NEW
│   ├── main.py          # Main API application
│   ├── models.py        # Data models
│   ├── agents.py        # Agent templates
│   ├── services/        # Business logic
│   ├── k8s/            # Kubernetes manifests
│   ├── examples/       # Usage examples
│   └── docs/           # Documentation
├── frontend/           # Next.js frontend
└── tests/             # Test suite
```

## ✨ Key Features

### Backend (NEW)
- 🤖 **6 Pre-built Agent Templates** - Code Assistant, Data Analyst, Customer Support, etc.
- 🐳 **Automated Docker Builds** - Generates and builds containers automatically
- ☸️ **Kubernetes Deployment** - Auto-deploys to DigitalOcean K8s
- 📈 **Auto-scaling** - Horizontal Pod Autoscaling support
- 🔒 **SSL/HTTPS** - Automatic certificate management
- 📊 **Monitoring** - Health checks and logging
- 🎯 **REST API** - Complete deployment management

### Agent Templates
1. **Code Assistant** - Code generation, debugging, optimization
2. **Data Analyst** - Data analysis and visualization
3. **Customer Support** - Customer service automation
4. **Content Writer** - Creative content generation
5. **Research Assistant** - Research and Q&A
6. **General Assistant** - Multi-purpose AI

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
./quickstart.sh
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs for API documentation

### Deploy an Agent

```bash
# Using curl
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @backend/examples/single_agent.json

# Using Python
python backend/examples/example_deploy.py deploy backend/examples/single_agent.json
```

## 📚 Documentation

- **[Backend README](backend/README.md)** - Backend documentation
- **[Architecture Guide](backend/ARCHITECTURE.md)** - System architecture
- **[Deployment Guide](backend/DEPLOYMENT.md)** - Step-by-step deployment
- **[Project Summary](backend/PROJECT_SUMMARY.md)** - Complete overview

## 🛠 Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Next.js, React, TypeScript
- **Infrastructure**: DigitalOcean Kubernetes
- **Containerization**: Docker
- **AI/LLM**: OpenAI GPT-4o
- **Orchestration**: Kubernetes, NGINX Ingress

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/deploy` | POST | Deploy agents |
| `/deployments` | GET | List all deployments |
| `/deployments/{name}` | GET | Get deployment status |
| `/deployments/{name}` | DELETE | Delete deployment |
| `/templates` | GET | List available templates |
| `/health` | GET | Health check |

## 🔧 Configuration

Each agent is configured via JSON:

```json
{
  "name": "code-assistant",
  "template": "Code Assistant",
  "model": "OpenAI gpt-4o",
  "instruction": "You are a coding assistant",
  "resources": {
    "cpu": "500m",
    "memory": "512Mi"
  },
  "scaling": {
    "replicas": 2,
    "autoscale": true,
    "min_replicas": 2,
    "max_replicas": 10
  },
  "endpoints": ["generate", "debug"]
}
```

## 🌐 Deployment Flow

```
User Config → API Validation → Docker Build → Registry Push 
    → K8s Deployment → Live Agent Endpoint
```

## 💡 Usage Examples

See `backend/examples/` for:
- `single_agent.json` - Deploy one agent
- `deploy_multiple_agents.json` - Deploy multiple agents
- `example_deploy.py` - Python client script

## 🔐 Security

- Kubernetes Secrets for API keys
- RBAC (Role-Based Access Control)
- TLS/HTTPS encryption
- Non-root container execution
- Resource limits and quotas

## 📊 Monitoring

- Health check endpoints
- Liveness/readiness probes
- Horizontal Pod Autoscaling
- Structured logging
- Resource metrics

## 💰 Cost Estimate (DigitalOcean)

**Minimal**: ~$65/month (2-node cluster)
**Production**: ~$176/month (3-node cluster)
*Plus OpenAI API usage*

## 🤝 Contributing

Contributions welcome! Please see our contributing guidelines.

## 📝 License

MIT License

## 🙏 Acknowledgments

Built for efficient GenAI agent deployment and management.

---

**For detailed backend documentation, see [backend/README.md](backend/README.md)**

# ParagonAI-The-Null-Pointers
Canada DevOps Community of Practice Hackathon Toronto - Team 3 

Project Name - ParagonAI | The Null Pointers

Team Mentor - Kanwarpreet Singh Khurana

Participant Names - 

     Team Lead - George Farag
     Team Members - Aman Purohit, Hassan Elbaytam, Minh Pham, Siddharth Lamba

## Project setup
### Setup python enviroment
```bash
python -m venv .venv
pip install -r requirements.txt
```

### setp env credentials
```bash
cp .env.example .env
```

add groq api key to newly created .env file


