# Automation Skill

Create and manage OpenHands automations — tasks that run in sandboxes on a cron schedule or triggered by webhook events (GitHub, custom services).

## Triggers

This skill is activated by keywords:
- `automation` / `automations`
- `scheduled task`
- `cron job` / `cron schedule`
- `webhook` / `webhooks`
- `event trigger`
- `github event`
- `pull request automation`
- `issue automation`

## Features

- **Plugin-spec automations (preferred for reusable/code-backed work)**: Create automations from a plugin in a chosen local or remote git repo, with a manifest that declares its config schema, runtime profiles, entrypoint, and suggested trigger
- **Prompt-based creation**: Create one-off automations from a natural language prompt, for tasks that benefit from agent reasoning
- **Plugin preset automations**: Use plugin presets for prompt-driven plugin runs when no executable plugin-spec contract exists yet
- **Custom scripts**: Run your own code, with or without an LLM - the cheaper, more reliable fit for deterministic tasks (fixed data, scheduled HTTP calls, templated messages), and for custom dependencies or full control (see [references/custom-automation.md](references/custom-automation.md))
- **Event-triggered automations**: Trigger on GitHub events (PR opened, issue commented, push, etc.)
- **Custom webhooks**: Register webhooks for any service (Stripe, Slack, Linear, etc.)
- **JMESPath filters**: Match events based on payload content (labels, mentions, repos)
- **Automation management**: List, update, enable/disable, and delete automations
- **Manual dispatch**: Trigger automation runs on-demand

## API Base URL

Use an explicitly provided host first. When a local Agent Canvas automation server is running and no host is provided, use `http://localhost:8001/api/automation/v1`. Otherwise use the cloud default: `https://app.all-hands.dev/api/automation/v1`.

## Quick Start

Prefer plugin-spec automations for reusable or code-backed work. Before creating one, ask which local git repo or remote git repo should be used as the plugin source; if the user wants a local source and no repo exists yet, help initialize and commit one first. The examples below use the prompt preset, which still suits one-off tasks that need reasoning or judgment. For a deterministic task that needs no LLM, use a custom script instead — see the *Custom Script Example (No LLM)* in [SKILL.md](SKILL.md).

### Cron-Triggered Automation

```bash
curl -X POST "https://app.all-hands.dev/api/automation/v1/preset/prompt" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Report",
    "prompt": "Generate a daily status report and save it to the workspace",
    "trigger": {"type": "cron", "schedule": "0 9 * * 1-5", "timezone": "UTC"}
  }'
```

### Event-Triggered Automation (GitHub)

Respond to @openhands mentions in issue comments:

```bash
curl -X POST "https://app.all-hands.dev/api/automation/v1/preset/prompt" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mention Responder",
    "prompt": "Analyze the issue context and respond helpfully",
    "trigger": {
      "type": "event",
      "source": "github",
      "on": "issue_comment.created",
      "filter": "icontains(comment.body, '\''@openhands'\'')"
    }
  }'
```

Auto-review PRs with the "openhands" label:

```bash
curl -X POST "https://app.all-hands.dev/api/automation/v1/preset/prompt" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Auto Review PRs",
    "prompt": "Review this PR for code quality and best practices",
    "trigger": {
      "type": "event",
      "source": "github",
      "on": "pull_request.labeled",
      "filter": "contains(pull_request.labels[].name, '\''openhands'\'')"
    }
  }'
```

For preset and plugin-spec automations, the service handles SDK/runtime wiring, tarball packaging, upload, and automation creation automatically.

## See Also

- [SKILL.md](SKILL.md) — Full API reference, agent behavior rules, event keys, filters, and examples
- [references/custom-automation.md](references/custom-automation.md) — Reference for custom automations with user-provided scripts, SDK-based or deterministic (no LLM)
