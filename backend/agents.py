"""
Agent templates for different use cases
Each template provides a base configuration and Docker setup for specific agent types
"""

from typing import Dict, Any, List


class AgentTemplates:
    """Collection of agent templates"""
    
    TEMPLATES: Dict[str, Dict[str, Any]] = {
        "Code Assistant": {
            "description": "A coding assistant that helps with code generation, debugging, and optimization",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a coding assistant. Provide correct, optimized code with explanations.",
            "default_endpoints": ["generate", "debug", "optimize"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "python-dotenv==1.2.1"
            ],
            "entry_point": "code_assistant_server.py"
        },
        
        "Data Analyst": {
            "description": "An agent specialized in data analysis, visualization, and insights",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a data analyst. Analyze data, create visualizations, and provide insights.",
            "default_endpoints": ["analyze", "visualize", "insights"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "pandas==2.2.0",
                "numpy==1.26.4",
                "matplotlib==3.8.2",
                "python-dotenv==1.2.1"
            ],
            "entry_point": "data_analyst_server.py"
        },
        
        "Customer Support": {
            "description": "A customer support agent for handling queries and providing assistance",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a helpful customer support agent. Be friendly, professional, and solve customer issues.",
            "default_endpoints": ["chat", "ticket", "faq"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "python-dotenv==1.2.1"
            ],
            "entry_point": "customer_support_server.py"
        },
        
        "Content Writer": {
            "description": "An agent for generating creative content, articles, and marketing copy",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a creative content writer. Generate engaging, well-structured content.",
            "default_endpoints": ["generate", "rewrite", "summarize"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "python-dotenv==1.2.1"
            ],
            "entry_point": "content_writer_server.py"
        },
        
        "Research Assistant": {
            "description": "An agent for conducting research, summarizing papers, and answering questions",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a research assistant. Provide accurate, well-researched information with citations.",
            "default_endpoints": ["research", "summarize", "qa"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "python-dotenv==1.2.1",
                "beautifulsoup4==4.12.3",
                "requests==2.32.5"
            ],
            "entry_point": "research_assistant_server.py"
        },
        
        "General Assistant": {
            "description": "A general-purpose AI assistant for various tasks",
            "default_model": "OpenAI gpt-4o",
            "default_instruction": "You are a helpful AI assistant. Assist users with various tasks professionally.",
            "default_endpoints": ["generate", "chat"],
            "base_image": "python:3.11-slim",
            "requirements": [
                "fastapi==0.120.4",
                "uvicorn[standard]==0.34.0",
                "openai==2.6.1",
                "pydantic==2.10.5",
                "python-dotenv==1.2.1"
            ],
            "entry_point": "general_assistant_server.py"
        }
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> Dict[str, Any]:
        """Get template configuration by name"""
        if template_name not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(cls.TEMPLATES.keys())}")
        return cls.TEMPLATES[template_name]
    
    @classmethod
    def list_templates(cls) -> list:
        """List all available templates"""
        return [
            {
                "name": name,
                "description": config["description"],
                "default_model": config["default_model"],
                "endpoints": config["default_endpoints"]
            }
            for name, config in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def get_server_code(cls, template_name: str, agent_config: Any) -> str:
        """Generate FastAPI server code for the agent"""
        template = cls.get_template(template_name)
        
        return f'''"""
GenAI Agent Server: {agent_config.name}
Template: {template_name}
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import openai
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.{agent_config.logging.upper()})
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

app = FastAPI(title="{agent_config.name}", version="1.0.0")


class MessageRequest(BaseModel):
    """Request model for agent endpoints"""
    prompt: str
    context: Optional[str] = None
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7


class MessageResponse(BaseModel):
    """Response model for agent endpoints"""
    response: str
    model: str
    tokens_used: Optional[int] = None


@app.get("/")
async def root():
    return {{
        "agent": "{agent_config.name}",
        "template": "{template_name}",
        "model": "{agent_config.model}",
        "status": "running",
        "endpoints": {agent_config.endpoints + agent_config.customEndpoints}
    }}


@app.get("/health")
async def health():
    return {{"status": "healthy", "agent": "{agent_config.name}"}}


async def call_llm(prompt: str, context: Optional[str] = None, max_tokens: int = 2000, temperature: float = 0.7) -> Dict[str, Any]:
    """Call the LLM with the given prompt"""
    try:
        messages = [
            {{"role": "system", "content": """{agent_config.instruction}"""}}
        ]
        
        if context:
            messages.append({{"role": "system", "content": f"Context: {{context}}"'}})
        
        messages.append({{"role": "user", "content": prompt}})
        
        model_name = "{agent_config.model}".split()[-1]  # Extract model name from "OpenAI gpt-4o"
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {{
            "response": response.choices[0].message.content,
            "model": model_name,
            "tokens_used": response.usage.total_tokens
        }}
    except Exception as e:
        logger.error(f"LLM call failed: {{str(e)}}")
        raise HTTPException(status_code=500, detail=f"LLM call failed: {{str(e)}}")


{cls._generate_endpoint_handlers(agent_config.endpoints + agent_config.customEndpoints)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    @classmethod
    def _generate_endpoint_handlers(cls, endpoints: List[str]) -> str:
        """Generate endpoint handler code"""
        handlers = []
        
        for endpoint in endpoints:
            handler = f'''
@app.post("/{endpoint}", response_model=MessageResponse)
async def {endpoint}_endpoint(request: MessageRequest):
    """Handle {endpoint} requests"""
    try:
        result = await call_llm(
            prompt=request.prompt,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return MessageResponse(**result)
    except Exception as e:
        logger.error(f"{endpoint} endpoint failed: {{str(e)}}")
        raise HTTPException(status_code=500, detail=str(e))
'''
            handlers.append(handler)
        
        return "\n".join(handlers)
