#!/usr/bin/env python3
"""
Example script to deploy agents using the API
"""

import requests
import json
import os
from typing import List, Dict, Any


API_URL = os.getenv("API_URL", "http://localhost:8000")


def deploy_agents(agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deploy agents to the cluster"""
    print(f"🚀 Deploying {len(agents)} agent(s) to {API_URL}...")
    
    response = requests.post(
        f"{API_URL}/deploy",
        json=agents,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Deployment Status: {result['status']}")
        print(f"📝 Message: {result['message']}")
        
        for deployment in result['deployments']:
            print(f"\n📦 Agent: {deployment['agent_name']}")
            print(f"   Status: {deployment['status']}")
            if deployment['status'] == 'success':
                print(f"   Image: {deployment.get('image', 'N/A')}")
                print(f"   Endpoints: {', '.join(deployment.get('endpoints', []))}")
            else:
                print(f"   Error: {deployment.get('error', 'Unknown error')}")
        
        return result
    else:
        print(f"❌ Deployment failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def list_deployments() -> List[Dict[str, Any]]:
    """List all deployments"""
    print(f"\n📋 Listing deployments from {API_URL}...")
    
    response = requests.get(f"{API_URL}/deployments")
    
    if response.status_code == 200:
        deployments = response.json()
        print(f"Found {len(deployments)} deployment(s):")
        
        for deployment in deployments:
            print(f"\n  • {deployment['name']}")
            print(f"    Namespace: {deployment['namespace']}")
            print(f"    Replicas: {deployment['ready_replicas']}/{deployment['replicas']}")
            print(f"    Status: {deployment['status']}")
        
        return deployments
    else:
        print(f"❌ Failed to list deployments: {response.status_code}")
        return []


def get_deployment_status(agent_name: str) -> Dict[str, Any]:
    """Get status of a specific deployment"""
    print(f"\n🔍 Getting status for {agent_name}...")
    
    response = requests.get(f"{API_URL}/deployments/{agent_name}")
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Agent: {status['name']}")
        print(f"   Status: {status['status']}")
        print(f"   Ready: {status['ready_replicas']}/{status['replicas']}")
        return status
    else:
        print(f"❌ Agent not found or error: {response.status_code}")
        return None


def delete_deployment(agent_name: str) -> bool:
    """Delete a deployment"""
    print(f"\n🗑️  Deleting {agent_name}...")
    
    response = requests.delete(f"{API_URL}/deployments/{agent_name}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ Failed to delete: {response.status_code}")
        return False


def list_templates() -> List[Dict[str, Any]]:
    """List available templates"""
    print(f"\n📚 Listing available templates...")
    
    response = requests.get(f"{API_URL}/templates")
    
    if response.status_code == 200:
        result = response.json()
        templates = result['templates']
        print(f"Found {len(templates)} template(s):")
        
        for template in templates:
            print(f"\n  • {template['name']}")
            print(f"    Description: {template['description']}")
            print(f"    Default Model: {template['default_model']}")
            print(f"    Endpoints: {', '.join(template['endpoints'])}")
        
        return templates
    else:
        print(f"❌ Failed to list templates: {response.status_code}")
        return []


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python example_deploy.py deploy <config.json>")
        print("  python example_deploy.py list")
        print("  python example_deploy.py status <agent-name>")
        print("  python example_deploy.py delete <agent-name>")
        print("  python example_deploy.py templates")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "deploy":
        if len(sys.argv) < 3:
            print("❌ Please provide config file path")
            sys.exit(1)
        
        config_file = sys.argv[2]
        with open(config_file, 'r') as f:
            agents = json.load(f)
        
        # Ensure agents is a list
        if isinstance(agents, dict):
            agents = [agents]
        
        deploy_agents(agents)
    
    elif command == "list":
        list_deployments()
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("❌ Please provide agent name")
            sys.exit(1)
        
        agent_name = sys.argv[2]
        get_deployment_status(agent_name)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Please provide agent name")
            sys.exit(1)
        
        agent_name = sys.argv[2]
        delete_deployment(agent_name)
    
    elif command == "templates":
        list_templates()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
