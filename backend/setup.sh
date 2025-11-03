#!/bin/bash

# Setup script for the GenAI Agent Deployment Backend

set -e

echo "🚀 Setting up GenAI Agent Deployment Backend..."

# Check if required tools are installed
echo "📋 Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "⚠️  kubectl not found. Installing..." && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl" && chmod +x kubectl && sudo mv kubectl /usr/local/bin/; }

echo "✅ Prerequisites checked"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r ../requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your actual credentials"
else
    echo "✅ .env file already exists"
fi

# Login to DigitalOcean (interactive)
echo "🔐 DigitalOcean Configuration..."
read -p "Do you want to configure DigitalOcean access now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your DigitalOcean API token: " DO_TOKEN
    
    # Login to DigitalOcean
    doctl auth init --access-token "$DO_TOKEN"
    
    # Get cluster info
    echo "📋 Available Kubernetes clusters:"
    doctl kubernetes cluster list
    
    read -p "Enter your cluster ID: " CLUSTER_ID
    
    # Download kubeconfig
    doctl kubernetes cluster kubeconfig save "$CLUSTER_ID"
    
    echo "✅ DigitalOcean configured"
fi

# Configure Docker registry
echo "🐳 Docker Registry Configuration..."
read -p "Do you want to configure Docker registry access? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your Docker registry URL (e.g., registry.digitalocean.com/your-registry): " REGISTRY
    
    # Login to Docker registry
    doctl registry login
    
    echo "✅ Docker registry configured"
fi

# Create Kubernetes namespace
echo "☸️  Kubernetes Configuration..."
read -p "Do you want to create the Kubernetes namespace now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl create namespace genai-agents --dry-run=client -o yaml | kubectl apply -f -
    
    # Create OpenAI API key secret
    read -p "Enter your OpenAI API key: " OPENAI_KEY
    kubectl create secret generic openai-credentials \
        --from-literal=api-key="$OPENAI_KEY" \
        --namespace=genai-agents \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo "✅ Kubernetes configured"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the development server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "To build and run with Docker:"
echo "  docker build -t genai-deployment-backend ."
echo "  docker run -p 8000:8000 --env-file .env genai-deployment-backend"
echo ""
