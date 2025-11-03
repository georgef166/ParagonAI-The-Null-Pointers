import subprocess, shlex
from pathlib import Path

def run(cmd: str) -> tuple[int, str, str]:
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def kubectl_apply(manifest_file: Path) -> tuple[bool, str]:
    code, out, err = run(f"kubectl apply -f {manifest_file}")
    ok = (code == 0)
    return ok, out if ok else err
