from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import yaml
from .config import get_settings

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "k8s" / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(enabled_extensions=("j2",))
)

def render_manifest(template_name: str, context: dict) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)

def dump_yaml(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False)

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
