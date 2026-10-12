# Hello World Automation Plugin

A minimal example of the proposed executable automation plugin format.

The automation service reads `automation-plugin.json`, validates the required
profile and plugin-owned config defaults, then runs `python3 scripts/main.py`
with runtime metadata exposed through environment variables and config files.

The script is intentionally deterministic and does not start an agent
conversation. It prints the plugin-owned message and the agent profile name when
the runtime provides one.

The manifest also demonstrates `runtime.agent_profile.allowed_tools`: the automation service should reject an agent profile that enables any explicit tool outside this allowlist during validation.
