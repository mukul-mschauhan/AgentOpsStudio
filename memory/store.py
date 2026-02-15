from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict


MEMORY_FILE = Path("memory/session_memory.json")


def _resolve_memory_file() -> Path:
    """Return a writable memory file path.

    Streamlit Cloud can run from a read-only project mount in some setups, so we
    fall back to the system temp directory when local writes fail.
    """
    try:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        test_file = MEMORY_FILE.parent / ".write_test"
        test_file.write_text("ok")
        test_file.unlink(missing_ok=True)
        return MEMORY_FILE
    except OSError:
        return Path(tempfile.gettempdir()) / "agentops_session_memory.json"


def load_memory() -> Dict[str, Any]:
    memory_file = _resolve_memory_file()
    if not memory_file.exists():
        return {}
    try:
        return json.loads(memory_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def update_memory(patch: Dict[str, Any]) -> Dict[str, Any]:
    mem = load_memory()
    mem.update(patch)
    memory_file = _resolve_memory_file()
    try:
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        memory_file.write_text(json.dumps(mem, indent=2))
    except OSError:
        # Non-fatal; app should still continue even if persistence is unavailable.
        pass
    return mem
