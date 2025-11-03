#!/bin/bash

# Deploy the backend to DigitalOcean Kubernetes

set -e

echo "🚀 Deploying GenAI Deployment Backend to Kubernetes..."

# Variables
REGISTRY="${DOCKER_REGISTRY:-registry.digitalocean.com}"
NAMESPACE="${DOCKER_REGISTRY_NAMESPACE:-genai-agents}"
IMAGE_NAME="$REGISTRY/$NAMESPACE/deployment-backend"
VERSION="${1:-latest}"

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t "$IMAGE_NAME:$VERSION" .

# Tag as latest
docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"

# Login to DigitalOcean Container Registry
echo "🔐 Logging in to DigitalOcean Container Registry..."
doctl registry login

# Push image
echo "📤 Pushing image to registry..."
docker push "$IMAGE_NAME:$VERSION"
docker push "$IMAGE_NAME:latest"

# Create namespace if it doesn't exist
echo "☸️  Creating namespace..."
kubectl create namespace genai-agents --dry-run=client -o yaml | kubectl apply -f -

# Create secrets (prompt for values if not set)
echo "🔒 Setting up secrets..."

if [ -z "$OPENAI_API_KEY" ]; then
    read -p "Enter OpenAI API key: " OPENAI_API_KEY
fi

if [ -z "$DO_API_TOKEN" ]; then
    read -p "Enter DigitalOcean API token: " DO_API_TOKEN
fi

kubectl create secret generic backend-credentials \
    --from-literal=openai-api-key="$OPENAI_API_KEY" \
    --from-literal=do-api-token="$DO_API_TOKEN" \
    --namespace=genai-agents \
    --dry-run=client -o yaml | kubectl apply -f -

# Create kubeconfig secret
kubectl create secret generic kubeconfig \
    --from-file=config=$HOME/.kube/config \
    --namespace=genai-agents \
    --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
echo "📋 Applying Kubernetes manifests..."
kubectl apply -f k8s/deployment.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/genai-deployment-backend -n genai-agents --timeout=5m

# Get service URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service endpoints:"
kubectl get ingress -n genai-agents
echo ""
echo "To check pod status:"
echo "  kubectl get pods -n genai-agents"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/genai-deployment-backend -n genai-agents"
echo ""
