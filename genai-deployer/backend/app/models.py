from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResourceSpec(BaseModel):
    cpu: str = Field("500m", description="CPU request/limit")
    memory: str = Field("512Mi", description="Memory request/limit")

class ScalingSpec(BaseModel):
    replicas: int = 1
    autoscale: bool = False
    minReplicas: Optional[int] = 1
    maxReplicas: Optional[int] = 3
    targetCPUUtilizationPercentage: Optional[int] = 70

class EnvVar(BaseModel):
    name: str
    value: str

class AgentConfig(BaseModel):
    name: str
    template: Optional[str] = None
    model: str = "OpenAI gpt-4o"
    instruction: str = "You are a coding assistant. Provide correct, optimized code."
    resources: ResourceSpec = ResourceSpec()
    scaling: ScalingSpec = ScalingSpec()
    endpoints: List[str] = Field(default_factory=lambda: ["generate"])
    customEndpoints: List[str] = Field(default_factory=list)
    env: List[EnvVar] = Field(default_factory=list)
    logging: str = "info"
    cloud: Optional[str] = None
    integrations: Dict[str, Any] = Field(default_factory=dict)

class DeployResult(BaseModel):
    name: str
    manifest_paths: List[str]
    applied: bool
    message: str

class DeployResponse(BaseModel):
    results: List[DeployResult]
