"""
Kubernetes service for deploying and managing agents on DigitalOcean Kubernetes
"""

import os
import logging
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import json
from datetime import datetime

from models import AgentConfig, DeploymentStatus

logger = logging.getLogger(__name__)


class KubernetesService:
    """Service for managing Kubernetes deployments"""
    
    def __init__(self):
        self.namespace = os.getenv("K8S_NAMESPACE", "default")
        self.kubeconfig = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))
        self.cluster_name = os.getenv("K8S_CLUSTER_NAME", "genai-agents-cluster")
        logger.info(f"Kubernetes service initialized. Namespace: {self.namespace}")
    
    async def check_connection(self) -> Dict[str, Any]:
        """Check Kubernetes cluster connection"""
        try:
            result = subprocess.run(
                ["kubectl", "cluster-info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "connected": True,
                    "cluster": self.cluster_name,
                    "namespace": self.namespace
                }
            else:
                return {
                    "connected": False,
                    "error": result.stderr
                }
        except Exception as e:
            logger.error(f"Failed to check Kubernetes connection: {str(e)}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def generate_manifests(self, config: AgentConfig, image_name: str) -> Dict[str, Any]:
        """
        Generate Kubernetes manifests for agent deployment
        
        Args:
            config: Agent configuration
            image_name: Docker image name
            
        Returns:
            Dictionary containing all Kubernetes manifests
        """
        manifests = {
            "deployment": self._generate_deployment(config, image_name),
            "service": self._generate_service(config),
        }
        
        # Add HPA if autoscaling is enabled
        if config.scaling.autoscale:
            manifests["hpa"] = self._generate_hpa(config)
        
        # Add ingress for external access
        manifests["ingress"] = self._generate_ingress(config)
        
        return manifests
    
    def _generate_deployment(self, config: AgentConfig, image_name: str) -> Dict[str, Any]:
        """Generate Deployment manifest"""
        
        # Build environment variables
        env_vars = [
            {"name": "PORT", "value": "8080"},
            {"name": "LOG_LEVEL", "value": config.logging.upper()},
            {"name": "AGENT_NAME", "value": config.name},
        ]
        
        # Add OpenAI API key from secret
        env_vars.append({
            "name": "OPENAI_API_KEY",
            "valueFrom": {
                "secretKeyRef": {
                    "name": "openai-credentials",
                    "key": "api-key"
                }
            }
        })
        
        # Add custom environment variables
        for env in config.env:
            env_vars.append({"name": env.name, "value": env.value})
        
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "template": config.template.lower().replace(" ", "-"),
                    "managed-by": "genai-deployment-api"
                }
            },
            "spec": {
                "replicas": config.scaling.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name,
                            "template": config.template.lower().replace(" ", "-")
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": config.name,
                            "image": image_name,
                            "imagePullPolicy": "Always",
                            "ports": [{
                                "containerPort": 8080,
                                "name": "http"
                            }],
                            "env": env_vars,
                            "resources": {
                                "requests": {
                                    "cpu": config.resources.cpu,
                                    "memory": config.resources.memory
                                },
                                "limits": {
                                    "cpu": config.resources.cpu,
                                    "memory": config.resources.memory
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        return deployment
    
    def _generate_service(self, config: AgentConfig) -> Dict[str, Any]:
        """Generate Service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": config.name,
                "namespace": self.namespace,
                "labels": {
                    "app": config.name
                }
            },
            "spec": {
                "type": "ClusterIP",
                "selector": {
                    "app": config.name
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8080,
                    "protocol": "TCP",
                    "name": "http"
                }]
            }
        }
    
    def _generate_hpa(self, config: AgentConfig) -> Dict[str, Any]:
        """Generate HorizontalPodAutoscaler manifest"""
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": config.name,
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.name
                },
                "minReplicas": config.scaling.min_replicas,
                "maxReplicas": config.scaling.max_replicas,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": config.scaling.target_cpu_percentage
                        }
                    }
                }]
            }
        }
    
    def _generate_ingress(self, config: AgentConfig) -> Dict[str, Any]:
        """Generate Ingress manifest"""
        domain = os.getenv("DOMAIN", "genai-agents.example.com")
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": config.name,
                "namespace": self.namespace,
                "annotations": {
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rewrite-target": "/$2"
                }
            },
            "spec": {
                "ingressClassName": "nginx",
                "tls": [{
                    "hosts": [domain],
                    "secretName": f"{config.name}-tls"
                }],
                "rules": [{
                    "host": domain,
                    "http": {
                        "paths": [{
                            "path": f"/{config.name}(/|$)(.*)",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": config.name,
                                    "port": {
                                        "number": 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
    
    async def deploy_agent(self, agent_name: str, manifests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy agent to Kubernetes cluster
        
        Args:
            agent_name: Name of the agent
            manifests: Kubernetes manifests
            
        Returns:
            Deployment information
        """
        try:
            logger.info(f"Deploying agent {agent_name} to Kubernetes")
            
            # Create namespace if it doesn't exist
            await self._ensure_namespace()
            
            # Apply each manifest
            for manifest_type, manifest in manifests.items():
                await self._apply_manifest(manifest)
                logger.info(f"Applied {manifest_type} for {agent_name}")
            
            # Get service endpoints
            endpoints = await self._get_service_endpoints(agent_name)
            
            return {
                "deployment_name": agent_name,
                "namespace": self.namespace,
                "endpoints": endpoints,
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy agent {agent_name}: {str(e)}")
            raise
    
    async def _ensure_namespace(self) -> None:
        """Ensure namespace exists"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "namespace", self.namespace],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Create namespace
                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {
                        "name": self.namespace
                    }
                }
                await self._apply_manifest(namespace_manifest)
                logger.info(f"Created namespace: {self.namespace}")
        except Exception as e:
            logger.error(f"Failed to ensure namespace: {str(e)}")
            raise
    
    async def _apply_manifest(self, manifest: Dict[str, Any]) -> None:
        """Apply Kubernetes manifest"""
        try:
            # Convert manifest to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Apply using kubectl
            result = subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=manifest_yaml,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"kubectl apply failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to apply manifest: {str(e)}")
            raise
    
    async def _get_service_endpoints(self, agent_name: str) -> List[str]:
        """Get service endpoints"""
        try:
            domain = os.getenv("DOMAIN", "genai-agents.example.com")
            base_url = f"https://{domain}/{agent_name}"
            
            # You could also query the actual service/ingress here
            return [base_url]
            
        except Exception as e:
            logger.warning(f"Failed to get endpoints: {str(e)}")
            return []
    
    async def list_deployments(self) -> List[DeploymentStatus]:
        """List all deployments in the namespace"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployments", "-n", self.namespace, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to list deployments: {result.stderr}")
            
            deployments_data = json.loads(result.stdout)
            deployments = []
            
            for item in deployments_data.get("items", []):
                metadata = item.get("metadata", {})
                spec = item.get("spec", {})
                status = item.get("status", {})
                
                deployments.append(DeploymentStatus(
                    name=metadata.get("name", ""),
                    namespace=metadata.get("namespace", ""),
                    replicas=spec.get("replicas", 0),
                    ready_replicas=status.get("readyReplicas", 0),
                    available_replicas=status.get("availableReplicas", 0),
                    status="Ready" if status.get("availableReplicas", 0) > 0 else "Pending",
                    created_at=metadata.get("creationTimestamp", ""),
                    image=spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image")
                ))
            
            return deployments
            
        except Exception as e:
            logger.error(f"Failed to list deployments: {str(e)}")
            raise
    
    async def get_deployment_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific deployment"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployment", agent_name, "-n", self.namespace, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            deployment_data = json.loads(result.stdout)
            status = deployment_data.get("status", {})
            spec = deployment_data.get("spec", {})
            
            return {
                "name": agent_name,
                "namespace": self.namespace,
                "replicas": spec.get("replicas", 0),
                "ready_replicas": status.get("readyReplicas", 0),
                "available_replicas": status.get("availableReplicas", 0),
                "status": "Ready" if status.get("availableReplicas", 0) > 0 else "Pending"
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            raise
    
    async def delete_deployment(self, agent_name: str) -> Dict[str, Any]:
        """Delete a deployment and associated resources"""
        try:
            resources = ["deployment", "service", "hpa", "ingress"]
            deleted = []
            
            for resource in resources:
                result = subprocess.run(
                    ["kubectl", "delete", resource, agent_name, "-n", self.namespace],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    deleted.append(resource)
                    logger.info(f"Deleted {resource}/{agent_name}")
            
            return {
                "deleted": deleted,
                "agent": agent_name
            }
            
        except Exception as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            raise
