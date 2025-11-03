from pydantic import BaseModel
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    registry: str = os.getenv("REGISTRY", "registry.hub.docker.com/your-user")
    image_tag: str = os.getenv("IMAGE_TAG", "latest")
    kube_namespace: str = os.getenv("KUBE_NAMESPACE", "genai")
    use_ingress: bool = os.getenv("USE_INGRESS", "true").lower() == "true"
    ingress_class: str = os.getenv("INGRESS_CLASS", "nginx")
    base_domain: str | None = os.getenv("BASE_DOMAIN", None)
    default_agent_image: str = os.getenv("DEFAULT_AGENT_IMAGE", "")
    default_log_level: str = os.getenv("DEFAULT_LOG_LEVEL", "info")

    # Optional: pass OPENAI_API_KEY down to agent runtimes via K8s Secret separately in prod
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.default_agent_image:
        s.default_agent_image = f"{s.registry}/genai-agent-runtime:{s.image_tag}"
    return s
