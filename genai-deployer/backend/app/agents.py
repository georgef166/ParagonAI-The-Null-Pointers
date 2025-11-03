# Agent templates you can extend. 'template' in AgentConfig selects one of these, and the
# FastAPI backend fills any missing fields from the template.

AGENT_TEMPLATES = {
    "Code Assistant": {
        "instruction": "You are a coding assistant. Provide correct, optimized code.",
        "model": "OpenAI gpt-4o",
        "resources": {"cpu": "500m", "memory": "512Mi"},
        "endpoints": ["generate"],
        "logging": "info",
    },
    "Q&A": {
        "instruction": "Answer questions clearly and concisely.",
        "model": "OpenAI gpt-4o-mini",
        "resources": {"cpu": "250m", "memory": "256Mi"},
        "endpoints": ["generate"],
        "logging": "info",
    }
}

def apply_template(cfg: dict) -> dict:
    tname = cfg.get("template")
    if not tname:
        return cfg
    tmpl = AGENT_TEMPLATES.get(tname, {})
    merged = {**tmpl, **cfg}
    # Deep-merge simple nested dicts (like resources)
    if "resources" in tmpl:
        merged["resources"] = {**tmpl["resources"], **cfg.get("resources", {})}
    return merged
