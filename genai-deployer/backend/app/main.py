from fastapi import FastAPI, UploadFile, File, Body
from typing import List
import json
from pathlib import Path
from .models import AgentConfig, DeployResponse, DeployResult
from .deployer import render_agent_manifests
from .do import kubectl_apply

app = FastAPI(title="GenAI Agent Deployer")

MANIFEST_OUT = Path("/tmp/agent_manifests")
MANIFEST_OUT.mkdir(parents=True, exist_ok=True)

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/deploy", response_model=DeployResponse)
async def deploy_agents(
    files: List[UploadFile] | None = File(default=None, description="Upload multiple agent.config.json files"),
    agents_json: List[AgentConfig] | None = Body(default=None, description="Alternatively, send a JSON array of agent configs")
):
    # Accept either uploaded files OR JSON list
    agents: List[AgentConfig] = []
    if files:
        for uf in files:
            data = json.loads((await uf.read()).decode("utf-8"))
            agents.append(AgentConfig(**data))
    elif agents_json:
        agents = agents_json
    else:
        return DeployResponse(results=[DeployResult(name="(none)", manifest_paths=[], applied=False, message="No input provided")])

    # Render manifests and apply
    results: List[DeployResult] = []
    for agent in agents:
        out_dir = MANIFEST_OUT / agent.name
        out_dir.mkdir(parents=True, exist_ok=True)
        files = render_agent_manifests(agent, out_dir)

        applied_all = True
        messages = []
        for f in files:
            ok, msg = kubectl_apply(f)
            applied_all = applied_all and ok
            messages.append(msg.strip())
        results.append(DeployResult(
            name=agent.name,
            manifest_paths=[str(p) for p in files],
            applied=applied_all,
            message="\n".join(messages)
        ))

    return DeployResponse(results=results)
