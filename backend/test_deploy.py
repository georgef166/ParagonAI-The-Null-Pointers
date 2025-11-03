#!/usr/bin/env python3
"""
Test script to deploy multiple agents to DigitalOcean
"""

import requests
import json
import time
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:8000"


def deploy_agents(agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deploy multiple agents"""
    print(f"\n🚀 Deploying {len(agents)} agent(s)...")
    
    response = requests.post(
        f"{API_BASE_URL}/deploy",
        json=agents,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📝 Message: {result['message']}")
        
        for deployment in result['deployments']:
            print(f"\n  Agent: {deployment['agent_name']}")
            print(f"  Status: {deployment['status']}")
            if deployment['status'] == 'success':
                print(f"  Image: {deployment.get('image', 'N/A')}")
                print(f"  Endpoints: {', '.join(deployment.get('endpoints', []))}")
            else:
                print(f"  Error: {deployment.get('error', 'Unknown error')}")
        
        return result
    else:
        print(f"❌ Deployment failed: {response.status_code}")
        print(response.text)
        return None


def list_deployments() -> List[Dict[str, Any]]:
    """List all deployed agents"""
    print("\n📋 Listing deployments...")
    
    response = requests.get(f"{API_BASE_URL}/deployments")
    
    if response.status_code == 200:
        deployments = response.json()
        print(f"✅ Found {len(deployments)} deployment(s)")
        
        for dep in deployments:
            print(f"\n  Name: {dep['name']}")
            print(f"  Status: {dep['status']}")
            print(f"  Replicas: {dep['ready_replicas']}/{dep['replicas']}")
            print(f"  Image: {dep.get('image', 'N/A')}")
        
        return deployments
    else:
        print(f"❌ Failed to list deployments: {response.status_code}")
        return []


def get_deployment_status(agent_name: str) -> Dict[str, Any]:
    """Get status of a specific deployment"""
    print(f"\n🔍 Getting status for {agent_name}...")
    
    response = requests.get(f"{API_BASE_URL}/deployments/{agent_name}")
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Status: {status['status']}")
        print(f"  Replicas: {status['ready_replicas']}/{status['replicas']}")
        return status
    elif response.status_code == 404:
        print(f"❌ Agent {agent_name} not found")
        return None
    else:
        print(f"❌ Failed to get status: {response.status_code}")
        return None


def delete_deployment(agent_name: str) -> bool:
    """Delete a deployment"""
    print(f"\n🗑️  Deleting {agent_name}...")
    
    response = requests.delete(f"{API_BASE_URL}/deployments/{agent_name}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ Failed to delete: {response.status_code}")
        return False


def list_templates() -> List[str]:
    """List available agent templates"""
    print("\n📚 Available templates:")
    
    response = requests.get(f"{API_BASE_URL}/templates")
    
    if response.status_code == 200:
        templates = response.json()['templates']
        for template in templates:
            print(f"  - {template}")
        return templates
    else:
        print(f"❌ Failed to list templates: {response.status_code}")
        return []


def main():
    """Main test function"""
    print("=" * 60)
    print("GenAI Agent Deployment Test")
    print("=" * 60)
    
    # Check API health
    print("\n🏥 Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy")
            print(f"  Kubernetes: {'Connected' if health.get('kubernetes', {}).get('connected') else 'Disconnected'}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("\nMake sure the backend is running:")
        print("  cd backend")
        print("  ./venv/bin/python -m uvicorn main:app --reload --port 8000")
        return
    
    # List available templates
    list_templates()
    
    # Example: Deploy multiple agents
    print("\n" + "=" * 60)
    print("Test 1: Deploy Multiple Agents")
    print("=" * 60)
    
    agents = [
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
                "autoscale": False
            },
            "endpoints": ["generate"],
            "customEndpoints": [],
            "env": [],
            "logging": "info",
            "cloud": "DigitalOcean",
            "integrations": {}
        },
        {
            "name": "data-analyst",
            "template": "Data Analyst",
            "model": "OpenAI gpt-4o",
            "instruction": "You are a data analyst. Help analyze data and create visualizations.",
            "resources": {
                "cpu": "1",
                "memory": "1Gi"
            },
            "scaling": {
                "replicas": 2,
                "autoscale": True,
                "min_replicas": 1,
                "max_replicas": 5,
                "target_cpu_percentage": 70
            },
            "endpoints": ["analyze", "generate"],
            "customEndpoints": [],
            "env": [],
            "logging": "info",
            "cloud": "DigitalOcean",
            "integrations": {}
        },
        {
            "name": "customer-support",
            "template": "Customer Support",
            "model": "OpenAI gpt-4o",
            "instruction": "You are a helpful customer support agent. Be polite and professional.",
            "resources": {
                "cpu": "500m",
                "memory": "512Mi"
            },
            "scaling": {
                "replicas": 3,
                "autoscale": True,
                "min_replicas": 2,
                "max_replicas": 10,
                "target_cpu_percentage": 60
            },
            "endpoints": ["chat"],
            "customEndpoints": [],
            "env": [
                {"name": "SUPPORT_EMAIL", "value": "support@example.com"},
                {"name": "COMPANY_NAME", "value": "Acme Corp"}
            ],
            "logging": "debug",
            "cloud": "DigitalOcean",
            "integrations": {}
        }
    ]
    
    # Deploy agents
    result = deploy_agents(agents)
    
    if result and result['status'] != 'failed':
        # Wait a bit for deployments to settle
        print("\n⏳ Waiting 10 seconds for deployments to initialize...")
        time.sleep(10)
        
        # List all deployments
        print("\n" + "=" * 60)
        print("Test 2: List All Deployments")
        print("=" * 60)
        list_deployments()
        
        # Check individual status
        print("\n" + "=" * 60)
        print("Test 3: Check Individual Deployment Status")
        print("=" * 60)
        for agent in agents:
            get_deployment_status(agent['name'])
            time.sleep(1)
        
        # Optional: Clean up
        print("\n" + "=" * 60)
        print("Cleanup (Optional)")
        print("=" * 60)
        cleanup = input("\n⚠️  Do you want to delete the test deployments? (y/N): ")
        
        if cleanup.lower() == 'y':
            for agent in agents:
                delete_deployment(agent['name'])
                time.sleep(2)
            
            print("\n✅ Cleanup complete")
        else:
            print("\n📝 Deployments kept. Delete manually with:")
            for agent in agents:
                print(f"  curl -X DELETE {API_BASE_URL}/deployments/{agent['name']}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
