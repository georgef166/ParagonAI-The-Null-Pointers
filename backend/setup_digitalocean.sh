#!/bin/bash

# DigitalOcean Setup Script
# This script helps you set up DigitalOcean Container Registry and Kubernetes

set -e

echo "=============================================="
echo "DigitalOcean Setup for Agent Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if doctl is installed
echo "📋 Step 1: Checking prerequisites..."
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl CLI not found${NC}"
    echo ""
    echo "Please install doctl:"
    echo "  brew install doctl"
    echo ""
    echo "Or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi
echo -e "${GREEN}✅ doctl is installed${NC}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}⚠️  kubectl not found${NC}"
    echo "Install kubectl for Kubernetes management:"
    echo "  brew install kubectl"
else
    echo -e "${GREEN}✅ kubectl is installed${NC}"
fi
echo ""

# Authenticate with DigitalOcean
echo "📋 Step 2: Authenticating with DigitalOcean..."
echo ""
echo "You need a DigitalOcean API token."
echo "Get one from: https://cloud.digitalocean.com/account/api/tokens"
echo ""
read -p "Do you want to authenticate now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    doctl auth init
    echo -e "${GREEN}✅ Authentication successful${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping authentication. Run 'doctl auth init' manually.${NC}"
fi
echo ""

# Check/Create Container Registry
echo "📋 Step 3: Setting up Container Registry..."
echo ""

# Check if registry exists
REGISTRY_NAME="genai-agents"
if doctl registry get 2>/dev/null | grep -q "$REGISTRY_NAME"; then
    echo -e "${GREEN}✅ Registry '$REGISTRY_NAME' already exists${NC}"
else
    echo "Registry not found. Creating new registry..."
    read -p "Create registry '$REGISTRY_NAME'? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        doctl registry create "$REGISTRY_NAME"
        echo -e "${GREEN}✅ Registry created successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping registry creation${NC}"
    fi
fi
echo ""

# Login Docker to registry
echo "📋 Step 4: Logging Docker into DigitalOcean Registry..."
echo ""

if doctl registry login; then
    echo -e "${GREEN}✅ Docker authenticated with DigitalOcean registry${NC}"
else
    echo -e "${RED}❌ Failed to authenticate Docker${NC}"
    echo "Make sure Docker Desktop is running"
    exit 1
fi
echo ""

# Check/Create Kubernetes Cluster
echo "📋 Step 5: Kubernetes Cluster Setup..."
echo ""

CLUSTER_NAME="genai-agents-cluster"

# List existing clusters
echo "Checking for existing Kubernetes clusters..."
if doctl kubernetes cluster list 2>/dev/null | grep -q "$CLUSTER_NAME"; then
    echo -e "${GREEN}✅ Cluster '$CLUSTER_NAME' already exists${NC}"
    
    # Configure kubectl
    echo "Configuring kubectl..."
    doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
    echo -e "${GREEN}✅ kubectl configured${NC}"
else
    echo -e "${YELLOW}⚠️  No cluster named '$CLUSTER_NAME' found${NC}"
    echo ""
    echo "Would you like to create a Kubernetes cluster?"
    echo "  Name: $CLUSTER_NAME"
    echo "  Region: nyc1"
    echo "  Node size: 2 vCPU, 4 GB RAM"
    echo "  Node count: 2"
    echo "  Cost: ~$48/month"
    echo ""
    read -p "Create cluster? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating cluster (this takes 5-10 minutes)..."
        doctl kubernetes cluster create "$CLUSTER_NAME" \
            --region nyc1 \
            --version latest \
            --size s-2vcpu-4gb \
            --count 2
        
        echo -e "${GREEN}✅ Cluster created successfully${NC}"
        
        # Configure kubectl
        doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
        echo -e "${GREEN}✅ kubectl configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping cluster creation${NC}"
        echo "You can create one later with:"
        echo "  doctl kubernetes cluster create $CLUSTER_NAME --region nyc1 --size s-2vcpu-4gb --count 2"
    fi
fi
echo ""

# Create OpenAI secret
echo "📋 Step 6: Creating OpenAI API Key Secret..."
echo ""

if kubectl get secret openai-credentials &>/dev/null; then
    echo -e "${GREEN}✅ OpenAI secret already exists${NC}"
else
    echo "You need an OpenAI API key to run the agents."
    echo "Get one from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_KEY
    
    if [ -n "$OPENAI_KEY" ]; then
        kubectl create secret generic openai-credentials \
            --from-literal=api-key="$OPENAI_KEY"
        echo -e "${GREEN}✅ OpenAI secret created${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping OpenAI secret creation${NC}"
        echo "Create it later with:"
        echo "  kubectl create secret generic openai-credentials --from-literal=api-key=YOUR_KEY"
    fi
fi
echo ""

# Install NGINX Ingress Controller
echo "📋 Step 7: Installing NGINX Ingress Controller..."
echo ""

if kubectl get namespace ingress-nginx &>/dev/null; then
    echo -e "${GREEN}✅ NGINX Ingress already installed${NC}"
else
    echo "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml
    
    echo "Waiting for Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s || true
    
    echo -e "${GREEN}✅ NGINX Ingress installed${NC}"
fi
echo ""

# Get Load Balancer IP
echo "📋 Step 8: Getting Load Balancer IP..."
echo ""

echo "Waiting for Load Balancer to be assigned an IP..."
for i in {1..30}; do
    LB_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$LB_IP" ]; then
        echo -e "${GREEN}✅ Load Balancer IP: $LB_IP${NC}"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 5
done

if [ -z "$LB_IP" ]; then
    echo -e "${YELLOW}⚠️  Load Balancer IP not yet assigned${NC}"
    echo "Check later with:"
    echo "  kubectl get svc ingress-nginx-controller -n ingress-nginx"
else
    # Update .env file
    if [ -f ".env" ]; then
        echo ""
        echo "Updating .env file with Load Balancer IP..."
        if grep -q "^DOMAIN=" .env; then
            sed -i.bak "s|^DOMAIN=.*|DOMAIN=$LB_IP|" .env
            echo -e "${GREEN}✅ .env file updated${NC}"
        else
            echo "DOMAIN=$LB_IP" >> .env
            echo -e "${GREEN}✅ DOMAIN added to .env${NC}"
        fi
    fi
fi
echo ""

# Summary
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "  - DigitalOcean authenticated: ✓"
echo "  - Container Registry: registry.digitalocean.com/$REGISTRY_NAME"
echo "  - Docker logged in: ✓"
if kubectl cluster-info &>/dev/null; then
    echo "  - Kubernetes cluster: $CLUSTER_NAME (connected)"
else
    echo "  - Kubernetes cluster: Not connected"
fi
if [ -n "$LB_IP" ]; then
    echo "  - Load Balancer IP: $LB_IP"
fi
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Update your .env file with required credentials:"
echo "   - OPENAI_API_KEY=your-openai-api-key"
echo "   - DO_API_TOKEN=your-do-token"
if [ -n "$LB_IP" ]; then
    echo "   - DOMAIN=$LB_IP (already set)"
fi
echo ""
echo "2. Start the backend server:"
echo "   cd backend"
echo "   ./venv/bin/python -m uvicorn main:app --reload --port 8000"
echo ""
echo "3. Deploy your first agent:"
echo "   python test_deploy.py"
echo ""
echo "4. Your agents will be accessible at:"
if [ -n "$LB_IP" ]; then
    echo "   http://$LB_IP/AGENT_NAME/ENDPOINT"
else
    echo "   http://LOAD_BALANCER_IP/AGENT_NAME/ENDPOINT"
fi
echo ""
echo "📚 Documentation:"
echo "  - Quick Start: QUICKSTART.md"
echo "  - Full Setup: SETUP_GUIDE.md"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "=============================================="
