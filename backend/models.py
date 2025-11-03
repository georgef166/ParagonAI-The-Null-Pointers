"""
Pydantic models for agent configuration and deployment
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


class ResourceConfig(BaseModel):
    """Resource configuration for agent containers"""
    cpu: str = Field(default="500m", description="CPU allocation (e.g., 500m, 1, 2)")
    memory: str = Field(default="512Mi", description="Memory allocation (e.g., 512Mi, 1Gi)")


class ScalingConfig(BaseModel):
    """Scaling configuration for agent deployments"""
    replicas: int = Field(default=1, ge=1, le=10, description="Number of replicas")
    autoscale: bool = Field(default=False, description="Enable autoscaling")
    min_replicas: Optional[int] = Field(default=None, ge=1, description="Minimum replicas for autoscaling")
    max_replicas: Optional[int] = Field(default=None, ge=1, le=20, description="Maximum replicas for autoscaling")
    target_cpu_percentage: Optional[int] = Field(default=70, ge=1, le=100, description="Target CPU percentage for autoscaling")


class EnvVar(BaseModel):
    """Environment variable configuration"""
    name: str
    value: str


class AgentConfig(BaseModel):
    """
    Configuration for a GenAI agent deployment
    """
    name: str = Field(..., description="Unique agent name (used as deployment name)")
    template: str = Field(..., description="Template type (e.g., 'Code Assistant', 'Data Analyst')")
    model: str = Field(..., description="LLM model to use (e.g., 'OpenAI gpt-4o')")
    instruction: str = Field(..., description="System instruction/prompt for the agent")
    
    resources: ResourceConfig = Field(default_factory=ResourceConfig)
    scaling: ScalingConfig = Field(default_factory=ScalingConfig)
    
    endpoints: List[str] = Field(default_factory=list, description="Standard endpoints to enable")
    customEndpoints: List[str] = Field(default_factory=list, description="Custom endpoints")
    
    env: List[EnvVar] = Field(default_factory=list, description="Environment variables")
    
    logging: Literal["debug", "info", "warning", "error"] = Field(default="info")
    cloud: str = Field(default="DigitalOcean", description="Cloud provider")
    integrations: Dict[str, Any] = Field(default_factory=dict, description="Third-party integrations")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name for Kubernetes compatibility"""
        if not v:
            raise ValueError("Agent name cannot be empty")
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Agent name must contain only alphanumeric characters, hyphens, and underscores")
        if len(v) > 63:
            raise ValueError("Agent name must be 63 characters or less")
        return v.lower().replace('_', '-')
    
    @field_validator('scaling')
    @classmethod
    def validate_scaling(cls, v: ScalingConfig) -> ScalingConfig:
        """Validate scaling configuration"""
        if v.autoscale:
            if v.min_replicas is None or v.max_replicas is None:
                raise ValueError("min_replicas and max_replicas must be set when autoscale is enabled")
            if v.min_replicas > v.max_replicas:
                raise ValueError("min_replicas must be less than or equal to max_replicas")
        return v


class DeploymentInfo(BaseModel):
    """Information about a deployed agent"""
    agent_name: str
    status: Literal["success", "failed", "pending"]
    image: Optional[str] = None
    endpoints: Optional[List[str]] = None
    namespace: Optional[str] = "default"
    deployment_name: Optional[str] = None
    error: Optional[str] = None


class DeploymentResponse(BaseModel):
    """Response from deployment endpoint"""
    status: Literal["success", "failed", "partial"]
    message: str
    deployments: List[Dict[str, Any]]


class DeploymentStatus(BaseModel):
    """Status of a deployment in the cluster"""
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    status: str
    created_at: str
    image: Optional[str] = None
    endpoints: Optional[List[str]] = None
