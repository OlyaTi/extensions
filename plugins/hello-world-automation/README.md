# Hello World Automation Plugin

This is a minimal plugin-backed automation that uses the automation service stock runner.

The automation manifest points at a plugin command instead of a custom Python entrypoint:

```json
"entrypoint": {
  "runner": "conversation",
  "command": "hello"
}
```

At run time, the automation service packages the stock SDK runner. The runner loads this same plugin as a conversation plugin and sends `/hello-world-automation:hello` as the prompt. The command prompt lives in `commands/hello.md`.

The manifest also demonstrates `runtime.agent_profile.allowed_tools`: the automation service rejects an agent profile unless it explicitly enables exactly the tools the plugin allows. The same allowlist model applies to MCP server refs and secret refs when a plugin declares them.
