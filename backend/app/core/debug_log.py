from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict


def write_debug_log(
    *,
    hypothesis_id: str,
    location: str,
    message: str,
    data: Dict[str, Any] | None = None,
    run_id: str = "run1",
) -> None:
    """Write a debug log line only when DEBUG_LOG_PATH is set (e.g. during debugging)."""
    log_path = os.environ.get("DEBUG_LOG_PATH")
    if not log_path:
        return
    payload: Dict[str, Any] = {
        "id": f"log_{int(time.time() * 1000)}_{hypothesis_id}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data or {},
        "runId": run_id,
        "hypothesisId": hypothesis_id,
    }
    try:
        with Path(log_path).open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except OSError:
        pass

