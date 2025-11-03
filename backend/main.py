"""
FastAPI Backend for GenAI Agent Deployment
Accepts agent configurations and deploys them to DigitalOcean Kubernetes cluster
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import os
from dotenv import load_dotenv

from models import AgentConfig, DeploymentResponse, DeploymentStatus
from services.kubernetes_service import KubernetesService
from services.docker_service import DockerService
from services.agent_service import AgentService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GenAI Agent Deployment API",
    description="API for deploying GenAI agents to DigitalOcean Kubernetes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
kubernetes_service = KubernetesService()
docker_service = DockerService()
agent_service = AgentService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GenAI Agent Deployment API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        k8s_status = await kubernetes_service.check_connection()
        return {
            "status": "healthy",
            "kubernetes": k8s_status,
            "timestamp": os.environ.get("DEPLOYMENT_TIMESTAMP", "unknown")
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


@app.post("/deploy", response_model=DeploymentResponse)
async def deploy_agents(agents: List[AgentConfig]):
    """
    Deploy multiple GenAI agents to Kubernetes cluster
    
    Args:
        agents: List of agent configurations
        
    Returns:
        DeploymentResponse with status and details for each agent
    """
    try:
        logger.info(f"Received deployment request for {len(agents)} agent(s)")
        
        deployment_results = []
        
        for agent in agents:
            try:
                logger.info(f"Processing agent: {agent.name}")
                
                # Validate agent configuration
                agent_service.validate_agent_config(agent)
                
                # Get agent template
                template = agent_service.get_template(agent.template)
                
                # Build Docker image for the agent
                image_name = await docker_service.build_agent_image(agent, template)
                logger.info(f"Built Docker image: {image_name}")
                
                # Push image to registry
                await docker_service.push_image(image_name)
                logger.info(f"Pushed image to registry: {image_name}")
                
                # Generate Kubernetes manifests
                manifests = kubernetes_service.generate_manifests(agent, image_name)
                logger.info(f"Generated Kubernetes manifests for {agent.name}")
                
                # Deploy to Kubernetes
                deployment_info = await kubernetes_service.deploy_agent(
                    agent.name, 
                    manifests
                )
                logger.info(f"Deployed {agent.name} to Kubernetes")
                
                deployment_results.append({
                    "agent_name": agent.name,
                    "status": "success",
                    "image": image_name,
                    "endpoints": deployment_info.get("endpoints", []),
                    "namespace": deployment_info.get("namespace", "default"),
                    "deployment_name": deployment_info.get("deployment_name")
                })
                
            except Exception as e:
                logger.error(f"Failed to deploy agent {agent.name}: {str(e)}")
                deployment_results.append({
                    "agent_name": agent.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Determine overall status
        failed_count = sum(1 for r in deployment_results if r["status"] == "failed")
        overall_status = "partial" if failed_count > 0 and failed_count < len(agents) else \
                        "failed" if failed_count == len(agents) else "success"
        
        return DeploymentResponse(
            status=overall_status,
            message=f"Deployed {len(agents) - failed_count}/{len(agents)} agents successfully",
            deployments=deployment_results
        )
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {str(e)}"
        )


@app.get("/deployments", response_model=List[DeploymentStatus])
async def list_deployments():
    """List all deployed agents"""
    try:
        deployments = await kubernetes_service.list_deployments()
        return deployments
    except Exception as e:
        logger.error(f"Failed to list deployments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {str(e)}"
        )


@app.get("/deployments/{agent_name}")
async def get_deployment_status(agent_name: str):
    """Get status of a specific agent deployment"""
    try:
        status = await kubernetes_service.get_deployment_status(agent_name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get deployment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment status: {str(e)}"
        )


@app.delete("/deployments/{agent_name}")
async def delete_deployment(agent_name: str):
    """Delete an agent deployment"""
    try:
        result = await kubernetes_service.delete_deployment(agent_name)
        return {
            "status": "success",
            "message": f"Agent {agent_name} deleted successfully",
            "details": result
        }
    except Exception as e:
        logger.error(f"Failed to delete deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deployment: {str(e)}"
        )


@app.get("/templates")
async def list_templates():
    """List available agent templates"""
    try:
        templates = agent_service.list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
