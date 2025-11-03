"""
Docker service for building and pushing agent container images
"""

import os
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import docker
from docker.errors import BuildError, APIError

from models import AgentConfig
from agents import AgentTemplates

logger = logging.getLogger(__name__)


class DockerService:
    """Service for building and pushing Docker images"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.registry = os.getenv("DOCKER_REGISTRY", "registry.digitalocean.com")
            self.registry_namespace = os.getenv("DOCKER_REGISTRY_NAMESPACE", "genai-agents")
            logger.info(f"Docker client initialized. Registry: {self.registry}/{self.registry_namespace}")
        except Exception as e:
            logger.warning(f"Docker client not available: {str(e)}")
            logger.warning("Docker operations will fail. Please start Docker Desktop to enable image building.")
            self.client = None
            self.registry = os.getenv("DOCKER_REGISTRY", "registry.digitalocean.com")
            self.registry_namespace = os.getenv("DOCKER_REGISTRY_NAMESPACE", "genai-agents")
    
    async def build_agent_image(self, config: AgentConfig, template: Dict[str, Any]) -> str:
        """
        Build Docker image for the agent
        
        Args:
            config: Agent configuration
            template: Template configuration
            
        Returns:
            Image name with tag
        """
        if not self.client:
            raise Exception("Docker client not available. Please start Docker Desktop.")
        
        try:
            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"Creating build context in {temp_dir}")
                
                # Generate server code
                server_code = AgentTemplates.get_server_code(template['name'] if 'name' in template else config.template, config)
                
                # Write server code
                server_file = Path(temp_dir) / template['entry_point']
                server_file.write_text(server_code)
                
                # Create requirements.txt
                requirements_file = Path(temp_dir) / "requirements.txt"
                requirements_file.write_text("\n".join(template['requirements']))
                
                # Create Dockerfile
                dockerfile_content = self._generate_dockerfile(config, template)
                dockerfile = Path(temp_dir) / "Dockerfile"
                dockerfile.write_text(dockerfile_content)
                
                # Create .env template
                env_file = Path(temp_dir) / ".env.template"
                env_vars = ["OPENAI_API_KEY=your-api-key-here"]
                env_vars.extend([f"{env.name}={env.value}" for env in config.env])
                env_file.write_text("\n".join(env_vars))
                
                # Build image
                image_tag = f"{self.registry}/{self.registry_namespace}/{config.name}:latest"
                logger.info(f"Building Docker image: {image_tag}")
                
                image, build_logs = self.client.images.build(
                    path=temp_dir,
                    tag=image_tag,
                    rm=True,
                    forcerm=True
                )
                
                # Log build output
                for log in build_logs:
                    if 'stream' in log:
                        logger.debug(log['stream'].strip())
                
                logger.info(f"Successfully built image: {image_tag}")
                return image_tag
                
        except BuildError as e:
            logger.error(f"Docker build failed: {str(e)}")
            raise Exception(f"Failed to build Docker image: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during image build: {str(e)}")
            raise
    
    async def push_image(self, image_name: str) -> None:
        """
        Push Docker image to registry
        
        Args:
            image_name: Full image name with tag
        """
        if not self.client:
            raise Exception("Docker client not available. Please start Docker Desktop.")
        
        try:
            logger.info(f"Pushing image to registry: {image_name}")
            
            # Push image
            push_logs = self.client.images.push(
                image_name,
                stream=True,
                decode=True
            )
            
            # Log push output
            for log in push_logs:
                if 'status' in log:
                    logger.debug(f"{log['status']}: {log.get('progress', '')}")
                if 'error' in log:
                    raise Exception(f"Push failed: {log['error']}")
            
            logger.info(f"Successfully pushed image: {image_name}")
            
        except APIError as e:
            logger.error(f"Failed to push image: {str(e)}")
            raise Exception(f"Failed to push Docker image: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during image push: {str(e)}")
            raise
    
    def _generate_dockerfile(self, config: AgentConfig, template: Dict[str, Any]) -> str:
        """Generate Dockerfile content"""
        return f'''FROM {template['base_image']}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY {template['entry_point']} .
COPY .env.template .env.template

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL={config.logging.upper()}

# Run the application
CMD ["python", "{template['entry_point']}"]
'''
