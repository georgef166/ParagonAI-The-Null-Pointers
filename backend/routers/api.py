# routers/api.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

class AgentConfig(BaseModel):
    name: str
    template: str
    model: str
    instruction: str
    resources: Dict[str, str]
    scaling: Dict[str, Any]
    endpoints: list = []
    customEndpoints: list = []
    env: list = []
    logging: str = "info"
    cloud: str = "None"
    integrations: dict = {}

class AgentDeploymentRequest(BaseModel):
    config: AgentConfig
    secrets: Optional[Dict[str, str]] = None

@router.post("/deploy/", status_code=status.HTTP_201_CREATED)
async def deploy_agent(request: AgentDeploymentRequest):
    """
    Deploy a new AI agent with the provided configuration and secrets.
    
    - **config**: Agent configuration including resources, scaling, etc.
    - **secrets**: Optional secrets to be injected as environment variables
    """
    try:
        from agent_manager import deploy_agent
        
        # Convert Pydantic model to dict
        config_dict = request.config.dict()
        
        # Deploy the agent
        result = deploy_agent(config_dict, request.secrets)
        
        if "error" in result.get("status", "").lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Agent deployment failed")
            )
            
        return {
            "status": "success",
            "data": result
        }
        
    except ImportError as e:
        logger.error(f"Agent deployment module not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Agent deployment not configured on this server"
        )
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy agent: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Add other existing endpoints...