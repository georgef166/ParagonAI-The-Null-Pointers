# Backend API

FastAPI backend service for deploying GenAI agents to DigitalOcean Kubernetes cluster.

## Features

- 🚀 Deploy multiple GenAI agents with a single API call
- 🎨 Multiple agent templates (Code Assistant, Data Analyst, Customer Support, etc.)
- 🐳 Automatic Docker image building and pushing
- ☸️ Kubernetes deployment with auto-scaling support
- 🔒 Secure credential management
- 📊 Deployment monitoring and management
- 🌐 Automatic ingress and endpoint configuration

## Architecture

```
User → FastAPI Backend → Docker Build → Docker Registry
                       → Kubernetes Deployment → Running Agent
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- kubectl
- DigitalOcean account with Kubernetes cluster
- OpenAI API key

### Installation

1. Run the setup script:
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

2. Update `.env` with your credentials:
```bash
cp .env.example .env
nano .env
```

3. Start the development server:
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Deploy Agents
```http
POST /deploy
Content-Type: application/json

[
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
    "env": [],
    "logging": "info"
  }
]
```

### List Deployments
```http
GET /deployments
```

### Get Deployment Status
```http
GET /deployments/{agent_name}
```

### Delete Deployment
```http
DELETE /deployments/{agent_name}
```

### List Templates
```http
GET /templates
```

### Health Check
```http
GET /health
```

## Agent Configuration

### Required Fields
- `name`: Unique agent identifier (alphanumeric, hyphens, max 63 chars)
- `template`: Template type (see available templates)
- `model`: LLM model (e.g., "OpenAI gpt-4o")
- `instruction`: System prompt for the agent

### Optional Fields
- `resources`: CPU and memory allocation
- `scaling`: Replica count and autoscaling settings
- `endpoints`: API endpoints to enable
- `customEndpoints`: Additional custom endpoints
- `env`: Environment variables
- `logging`: Log level (debug, info, warning, error)

## Available Templates

1. **Code Assistant** - Code generation, debugging, optimization
2. **Data Analyst** - Data analysis, visualization, insights
3. **Customer Support** - Customer queries and ticket handling
4. **Content Writer** - Creative content generation
5. **Research Assistant** - Research and Q&A
6. **General Assistant** - Multi-purpose assistant

## Docker Deployment

Build and run the backend in Docker:

```bash
docker build -t genai-deployment-backend .
docker run -p 8000:8000 --env-file .env genai-deployment-backend
```

## Kubernetes Deployment

Deploy the backend itself to Kubernetes:

```bash
# Build and push
docker build -t registry.digitalocean.com/your-registry/deployment-backend:latest .
docker push registry.digitalocean.com/your-registry/deployment-backend:latest

# Deploy
kubectl apply -f k8s/deployment.yaml
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port | No (default: 8000) |
| `K8S_NAMESPACE` | Kubernetes namespace | No (default: default) |
| `K8S_CLUSTER_NAME` | Cluster name | No |
| `DOCKER_REGISTRY` | Docker registry URL | Yes |
| `DOCKER_REGISTRY_NAMESPACE` | Registry namespace | Yes |
| `DO_API_TOKEN` | DigitalOcean API token | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `DOMAIN` | Base domain for ingress | No |

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── models.py              # Pydantic models
├── agents.py              # Agent templates
├── utils.py               # Utility functions
├── services/
│   ├── agent_service.py   # Agent management
│   ├── docker_service.py  # Docker operations
│   └── kubernetes_service.py  # K8s operations
├── Dockerfile             # Backend Docker image
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── setup.sh              # Setup script
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Troubleshooting

### Docker Build Fails
- Ensure Docker daemon is running
- Check Docker registry credentials
- Verify network connectivity

### Kubernetes Deployment Fails
- Verify kubeconfig is correct
- Check cluster connectivity: `kubectl cluster-info`
- Ensure namespace exists
- Verify RBAC permissions

### Agent Not Accessible
- Check ingress configuration
- Verify DNS settings
- Check service and pod status: `kubectl get pods,svc -n genai-agents`

## Security Notes

- Never commit `.env` file
- Use Kubernetes secrets for sensitive data
- Enable RBAC in production
- Use TLS/HTTPS for all endpoints
- Rotate API keys regularly

## License

MIT
