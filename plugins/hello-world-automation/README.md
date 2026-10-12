# Hello World Automation Plugin

A minimal example of the proposed executable automation plugin format.

The automation service reads `automation-plugin.json`, validates the required
profiles and config, then runs `python3 scripts/main.py` with the runtime
metadata exposed through environment variables and config files.

The script is intentionally deterministic and does not start an agent
conversation. It prints the configured message, plus the agent and LLM profile
names when the runtime provides them.
