#!/bin/bash

echo "🚀 Deploying test agent to DigitalOcean Kubernetes..."
echo ""

curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '[{
    "name": "code-assistant",
    "template": "Code Assistant",
    "model": "OpenAI gpt-4o",
    "instruction": "You are a helpful coding assistant. Provide clean, optimized code.",
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
  }]' | python3 -m json.tool

echo ""
echo "✅ Deployment request sent!"
echo ""
echo "Check status with:"
echo "  kubectl get pods"
echo "  kubectl get deployments"
echo "  kubectl get services"
echo "  kubectl get ingress"
