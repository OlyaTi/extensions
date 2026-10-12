#!/usr/bin/env python3
"""Example executable automation plugin entrypoint."""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_config() -> dict[str, Any]:
    config_path = os.environ.get("AUTOMATION_CONFIG_PATH")
    if not config_path:
        return {}
    path = Path(config_path)
    if not path.is_file():
        return {}
    with path.open() as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def fire_callback(status: str, error: str | None = None) -> None:
    callback_url = os.environ.get("AUTOMATION_CALLBACK_URL")
    if not callback_url:
        return
    token = os.environ.get("AUTOMATION_CALLBACK_API_KEY") or os.environ.get(
        "OPENHANDS_API_KEY", ""
    )
    body = {
        "status": status,
        "run_id": os.environ.get("AUTOMATION_RUN_ID"),
    }
    if error:
        body["error"] = error
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        callback_url,
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(
            f"Failed to send automation callback: HTTP {exc.code}: {detail}",
            file=sys.stderr,
        )
        raise
    except urllib.error.URLError as exc:
        print(f"Failed to send automation callback: {exc}", file=sys.stderr)
        raise


def main() -> None:
    config = load_config()
    message = config.get("message") or "Hello from the automation plugin"
    print(message)
    agent_profile = os.environ.get("AUTOMATION_AGENT_PROFILE_NAME")
    if agent_profile:
        print(f"Agent profile: {agent_profile}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        fire_callback("FAILED", str(exc))
        raise
    fire_callback("COMPLETED")
