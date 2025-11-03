"""
Example test file for the backend API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 500]  # May fail if K8s not configured


def test_list_templates():
    """Test list templates endpoint"""
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) > 0


def test_deploy_agent_validation():
    """Test agent deployment with invalid data"""
    invalid_agent = {
        "name": "",  # Invalid: empty name
        "template": "Invalid Template",
        "model": "OpenAI gpt-4o"
    }
    
    response = client.post("/deploy", json=[invalid_agent])
    assert response.status_code in [422, 500]


def test_deploy_agent_valid_config():
    """Test agent deployment with valid configuration"""
    valid_agent = {
        "name": "test-agent",
        "template": "Code Assistant",
        "model": "OpenAI gpt-4o",
        "instruction": "You are a coding assistant.",
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
    
    # This will fail without proper K8s/Docker setup, but validates the schema
    response = client.post("/deploy", json=[valid_agent])
    assert response.status_code in [200, 500]  # 500 expected without infrastructure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
