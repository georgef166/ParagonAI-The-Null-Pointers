from pathlib import Path
from typing import List, Dict, Any
from .models import AgentConfig, DeployResult
from .config import get_settings
from .agents import apply_template
from .k8s import render_manifest, write_file

def to_env_list(cfg_env: list[dict]) -> list[dict]:
    # Convert [{"name":"A","value":"B"}] -> same form for manifest
    return [{"name": e["name"], "value": e["value"]} for e in cfg_env]

def build_context(agent: AgentConfig) -> Dict[str, Any]:
    s = get_settings()
    name = agent.name
    # Ingress path per-agent; you can customize
    ingress_path = f"/agents/{name}"
    image = s.default_agent_image

    env_list = to_env_list([e.model_dump() for e in agent.env])

    # Core env for the runtime
    core_env = [
        {"name": "MODEL", "value": agent.model},
        {"name": "INSTRUCTION", "value": agent.instruction},
        {"name": "LOG_LEVEL", "value": agent.logging},
    ]
    env_all = core_env + env_list

    ctx = {
        "namespace": s.kube_namespace,
        "name": name,
        "image": image,
        "resources": {
            "cpu": agent.resources.cpu,
            "memory": agent.resources.memory
        },
        "replicas": agent.scaling.replicas,
        "ports": [{"name": "http", "containerPort": 8000}],
        "env": env_all,
        "use_ingress": s.use_ingress,
        "ingress_class": s.ingress_class,
        "base_domain": s.base_domain,
        "ingress_host": f"agents.{s.base_domain}" if s.base_domain else None,
        "ingress_path": ingress_path,
        "autoscale": agent.scaling.autoscale,
        "hpa": {
            "minReplicas": agent.scaling.minReplicas or 1,
            "maxReplicas": agent.scaling.maxReplicas or 3,
            "targetCPUUtilizationPercentage": agent.scaling.targetCPUUtilizationPercentage or 70
        }
    }
    return ctx

def render_agent_manifests(agent: AgentConfig, out_dir: Path) -> List[Path]:
    # Apply template defaults
    merged = apply_template(agent.model_dump())
    agent = AgentConfig(**merged)

    ctx = build_context(agent)
    files: List[Path] = []

    # Deployment
    dep_yaml = render_manifest("deployment.yaml.j2", ctx)
    dep_path = out_dir / f"{agent.name}-deployment.yaml"
    write_file(dep_path, dep_yaml)
    files.append(dep_path)

    # Service
    svc_yaml = render_manifest("service.yaml.j2", ctx)
    svc_path = out_dir / f"{agent.name}-service.yaml"
    write_file(svc_path, svc_yaml)
    files.append(svc_path)

    # Ingress (optional)
    if ctx["use_ingress"] and ctx["base_domain"]:
        ing_yaml = render_manifest("ingress.yaml.j2", ctx)
        ing_path = out_dir / f"{agent.name}-ingress.yaml"
        write_file(ing_path, ing_yaml)
        files.append(ing_path)

    # HPA (optional)
    if ctx["autoscale"]:
        hpa_yaml = render_manifest("hpa.yaml.j2", ctx)
        hpa_path = out_dir / f"{agent.name}-hpa.yaml"
        write_file(hpa_path, hpa_yaml)
        files.append(hpa_path)

    return files
