from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


MEMORY_FILE = Path("memory/session_memory.json")


def load_memory() -> Dict[str, Any]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(MEMORY_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def update_memory(patch: Dict[str, Any]) -> Dict[str, Any]:
    mem = load_memory()
    mem.update(patch)
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(mem, indent=2))
    return mem
