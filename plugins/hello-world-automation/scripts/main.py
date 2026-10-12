#!/usr/bin/env python3
"""Example executable automation plugin entrypoint."""

import json
import os
from pathlib import Path


def load_config() -> dict:
    config_path = os.environ.get("AUTOMATION_CONFIG_PATH")
    if not config_path:
        return {}
    path = Path(config_path)
    if not path.is_file():
        return {}
    with path.open() as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def main() -> None:
    config = load_config()
    message = config.get("message") or "Hello from the automation plugin"
    print(message)
    agent_profile = os.environ.get("AUTOMATION_AGENT_PROFILE_NAME")
    if agent_profile:
        print(f"Agent profile: {agent_profile}")


if __name__ == "__main__":
    main()
