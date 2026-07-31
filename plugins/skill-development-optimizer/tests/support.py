import importlib.util
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = (
    PLUGIN_ROOT / "skills" / "optimizing-skill-development" / "scripts"
)


def load_script(name: str):
    module_name = f"skill_optimizer_{name}"
    script_path = SCRIPTS_ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
