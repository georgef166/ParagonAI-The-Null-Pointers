# agent_manager.py
from typing import Dict, Any, Optional
import yaml
import subprocess
import os
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, config: Dict[str, Any], secrets: Optional[Dict[str, str]] = None):
        self.config = config
        self.secrets = secrets or {}
        self.name = config["name"]
        self.namespace = "ai-agents"
        self.ensure_namespace_exists()

    def ensure_namespace_exists(self):
        """Ensure the Kubernetes namespace exists."""
        try:
            subprocess.run(
                ["kubectl", "create", "namespace", self.namespace],
                capture_output=True,
                check=False
            )
        except Exception as e:
            logger.error(f"Error creating namespace: {e}")

    def create_kubernetes_manifest(self) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest with config and secrets."""
        # Environment variables from config
        env_vars = [
            {"name": "MODEL", "value": self.config["model"]},
            {"name": "INSTRUCTION", "value": self.config["instruction"]},
            {"name": "LOG_LEVEL", "value": self.config.get("logging", "info")}
        ]

        # Add secrets as environment variables
        for key, value in self.secrets.items():
            env_vars.append({
                "name": key,
                "value": value
            })

        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.name}-deployment",
                "namespace": self.namespace,
                "labels": {"app": self.name}
            },
            "spec": {
                "replicas": self.config["scaling"]["replicas"],
                "selector": {"matchLabels": {"app": self.name}},
                "template": {
                    "metadata": {
                        "labels": {"app": self.name},
                        "annotations": {
                            "config-hash": str(hash(json.dumps(self.config, sort_keys=True))),
                            "secrets-hash": str(hash(json.dumps(self.secrets, sort_keys=True))),
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": self.name,
                            "image": "your-ai-agent-image:latest",  # Replace with your actual image
                            "env": env_vars,
                            "ports": [{"containerPort": 8000}],
                            "resources": {
                                "requests": {
                                    "cpu": self.config["resources"]["cpu"],
                                    "memory": self.config["resources"]["memory"]
                                }
                            }
                        }]
                    }
                }
            }
        }

    def create_service_manifest(self) -> Dict[str, Any]:
        """Create Kubernetes service manifest."""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.name}-service",
                "namespace": self.namespace,
                "labels": {"app": self.name}
            },
            "spec": {
                "selector": {"app": self.name},
                "ports": [{
                    "protocol": "TCP",
                    "port": 80,
                    "targetPort": 8000
                }],
                "type": "LoadBalancer" if self.config.get("cloud") == "digitalocean" else "ClusterIP"
            }
        }

    def apply_kubernetes_manifests(self) -> Dict[str, Any]:
        """Apply the Kubernetes manifests and return the deployment status."""
        try:
            # Create temp directory for manifests
            temp_dir = Path("/tmp/agent-deployment")
            temp_dir.mkdir(exist_ok=True)
            
            # Write deployment and service manifests
            deployment = self.create_kubernetes_manifest()
            deployment_path = temp_dir / f"{self.name}-deployment.yaml"
            with open(deployment_path, 'w') as f:
                yaml.dump(deployment, f)
            
            service = self.create_service_manifest()
            service_path = temp_dir / f"{self.name}-service.yaml"
            with open(service_path, 'w') as f:
                yaml.dump(service, f)
            
            # Apply manifests
            subprocess.run(
                ["kubectl", "apply", "-f", str(deployment_path), "-n", self.namespace],
                check=True
            )
            subprocess.run(
                ["kubectl", "apply", "-f", str(service_path), "-n", self.namespace],
                check=True
            )
            
            # Get service URL
            service_info = subprocess.run(
                ["kubectl", "get", "svc", f"{self.name}-service", "-n", self.namespace, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            service_data = json.loads(service_info.stdout)
            
            return {
                "status": "success",
                "message": f"Agent {self.name} deployed successfully",
                "service": {
                    "name": f"{self.name}-service",
                    "namespace": self.namespace,
                    "endpoints": self.config.get("endpoints", []),
                    "url": self._get_service_url(service_data)
                }
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Kubernetes error: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Deployment failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _get_service_url(self, service_data: Dict) -> str:
        """Get the service URL based on the service type."""
        if self.config.get("cloud") == "digitalocean":
            # For LoadBalancer services in DigitalOcean
            try:
                ingress = service_data['status']['loadBalancer']['ingress'][0]
                return f"http://{ingress.get('hostname', ingress.get('ip', 'pending'))}"
            except (KeyError, IndexError):
                return "Service URL pending (check with kubectl get svc)"
        else:
            # For ClusterIP services
            return f"http://{self.name}-service.{self.namespace}.svc.cluster.local"

def deploy_agent(config: Dict[str, Any], secrets: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Deploy an agent with the given configuration and secrets."""
    try:
        # Validate required fields
        required_fields = ["name", "model", "resources", "scaling"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        manager = AgentManager(config, secrets)
        return manager.apply_kubernetes_manifests()
        
    except Exception as e:
        logger.error(f"Agent deployment failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }