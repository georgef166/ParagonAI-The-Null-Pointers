"""
Agent service for managing agent templates and configurations
"""

import logging
from typing import Dict, Any, List
from models import AgentConfig
from agents import AgentTemplates

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agent templates and validation"""
    
    def __init__(self):
        self.templates = AgentTemplates()
    
    def validate_agent_config(self, config: AgentConfig) -> None:
        """
        Validate agent configuration
        
        Args:
            config: Agent configuration to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check if template exists
        if config.template not in AgentTemplates.TEMPLATES:
            available = list(AgentTemplates.TEMPLATES.keys())
            raise ValueError(f"Invalid template '{config.template}'. Available: {available}")
        
        # Validate model format
        if not config.model:
            raise ValueError("Model must be specified")
        
        # Validate endpoints
        if not config.endpoints and not config.customEndpoints:
            raise ValueError("At least one endpoint must be specified")
        
        # Validate resources
        if not config.resources.cpu or not config.resources.memory:
            raise ValueError("CPU and memory resources must be specified")
        
        logger.info(f"Agent configuration validated successfully: {config.name}")
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get template configuration"""
        return self.templates.get_template(template_name)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return self.templates.list_templates()
    
    def generate_server_code(self, template_name: str, config: AgentConfig) -> str:
        """Generate FastAPI server code for the agent"""
        return self.templates.get_server_code(template_name, config)
