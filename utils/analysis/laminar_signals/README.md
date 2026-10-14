# Laminar Signal Analysis

## Local automation trace replay

`replay.py` is a small, stdlib-only prototype for comparing trace analyzers before
production rollout. It reads automation conversation spans from Laminar, freezes
a local sample, checks model evidence references, and optionally asks a coordinator
for testable improvement hypotheses. It makes no source edits or external writes
beyond model inference requests.

Supply credentials through the environment:

- `LMNR_PROJECT_API_KEY`: SQL-capable key for the intended project.
- `LMNR_BASE_URL`: API origin; defaults to Laminar Cloud.
- `LLM_API_KEY` and `LLM_BASE_URL`: OpenAI-compatible model endpoint.

The project key scopes SQL reads. `--project-id` records provenance and does not
grant access or select a different project's data. Use the intended project's key.

```bash
python utils/analysis/laminar_signals/replay.py fetch \
  --project-id PROJECT_UUID --output /private/local/snapshot.json \
  --app-url https://laminar.sh --limit 3 --max-spans 80

python utils/analysis/laminar_signals/replay.py analyze \
  --input /private/local/snapshot.json --output /private/local/luna.json \
  --model openai/gpt-6-luna --coordinator openai/gpt-6.1-sol
```

Run `analyze` with different `--model` values on the same snapshot to compare
latency, token usage, reported proxy cost, and findings. Omit `--coordinator` for
analyzer comparisons. Add repeatable `--source-file` arguments to ground the
coordinator in reviewed source. Model availability depends on the endpoint.
GPT-6 models use the Responses API with low reasoning effort by default; use
`--reasoning-effort` to compare supported settings. GPT-6.1 Sol rejects `none`.
Other providers use Chat Completions. Both endpoints must support forced function
output for the report schema.

Collection is sequential and limited to five conversations, seven days, 200 spans
per conversation, and two megabytes per response. It excludes recent conversation
starts, which does not prove completion. Session attribution uses span metadata
because a single trace can contain multiple conversations. Accumulated LLM inputs
are omitted; long span content and large conversations are explicitly truncated.
The snapshot records these limits. Treat conclusions from incomplete evidence as
provisional.

Credential/email redaction is best effort; review snapshots before sharing them.
Keep snapshots and reports outside version control. Output files are owner-only.
Each model request has an output/input limit; unknown span or finding references
fail validation. There are no automatic retries, deployments, or PR publications.
Reports contain model judgments and hypotheses, not evaluated improvements or
measured detector accuracy. Production budgets, durable scheduling/deduplication,
human-labeled evaluation, and source revision uptake remain subsequent work.

Analyze Laminar signal events using LLMs to identify issues and areas for improvement. Uses function calling to get structured output with clickable trace URLs.

**Primary Focus**: Identifying problems and generating actionable recommendations to improve AI agent behavior.

## Directory Structure

```
laminar_signals/
├── analyze.py          # Main analysis script
├── README.md           # This file
└── templates/
    ├── default.j2      # Generic template for any signal type
    └── pr_review.j2    # Specialized template for PR review signals
```

## Prerequisites

- Python 3.9+
- `jinja2` package

```bash
pip install jinja2
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LMNR_PROJECT_API_KEY` | Yes | - | Laminar project API key |
| `LMNR_PROJECT_ID` | No | - | Laminar project ID (for generating clickable trace URLs) |
| `LLM_API_KEY` | Yes | - | API key for the LLM |
| `LLM_MODEL` | No | `gemini-3-pro-preview` | Model to use |
| `LLM_BASE_URL` | No | `https://llm-proxy.app.all-hands.dev` | Base URL for LLM API |

**Note:** To enable clickable trace URLs in the output, set `LMNR_PROJECT_ID` to your Laminar project ID. 
You can find this in your Laminar dashboard URL: `https://laminar.sh/project/{PROJECT_ID}/...`

## Usage

```bash
# List available signals
python analyze.py --list-signals

# Analyze PR review signals (outputs markdown by default)
python analyze.py --signal "pr review suggestion and analysis"

# Analyze with skill context for grounded recommendations
python analyze.py --signal "pr review suggestion and analysis" \
    --skill-dir ../../../plugins/pr-review

# Output as JSON (structured data with trace URLs)
python analyze.py --signal "pr review suggestion and analysis" --format json

# Analyze with custom prompt template
python analyze.py --signal "my-signal" --prompt-file my_prompt.j2

# Analyze last 30 days and save to file
python analyze.py --signal "my-signal" --days 30 --output results.md
```

## How It Works

1. **Fetches Signals**: Queries the Laminar SQL API to retrieve signal events with trace IDs.

2. **Generates Prompt**: Uses a Jinja2 template focused on identifying issues and improvements.

3. **Loads Skill Context** (optional): If `--skill-dir` is provided, loads the skill/plugin content so recommendations can reference specific prompt verbiage.

4. **LLM Analysis**: Uses **function calling** to get structured output with:
   - `issues`: Problems and failures with severity, frequency, and clickable trace URLs
   - `recommendations`: Specific fixes with priority levels (grounded in skill content when provided)
   - `metrics`: Quantitative statistics (issue rate, etc.)
   - `strengths`: Brief note on what's working (secondary focus)

5. **Output**: Markdown report (default) or JSON for programmatic use.

## Grounding Recommendations in Skills

Use `--skill-dir` to provide the current skill/plugin configuration. This allows the LLM to:
- Reference specific sections of the prompt that need changes
- Suggest exact wording modifications
- Ground recommendations in the actual instructions the agent follows

```bash
# Use a skill directory
python analyze.py --signal "..." --skill-dir path/to/skills/code-review

# Use a plugin directory (loads nested skills and prompt.py)
python analyze.py --signal "..." --skill-dir path/to/plugins/pr-review
```

The script automatically loads:
- `SKILL.md` from the directory
- `scripts/prompt.py` if present (for plugins)
- Any nested skills in `skills/` subdirectory

## Output Structure

### Issues (Primary Focus)

Each issue includes:
- **Title**: Short description
- **Description**: Detailed explanation of the problem
- **Severity**: critical / high / medium / low
- **Frequency**: How often this occurs
- **Trace URLs**: Clickable links to example traces in Laminar

### Recommendations

Each recommendation includes:
- **Title**: Short description
- **Description**: How to implement the fix
- **Addresses**: Which issues this fixes
- **Priority**: high / medium / low

### Example JSON Output

```json
{
  "issues": [
    {
      "title": "Premature Approval of Functional Defects",
      "description": "The AI approves code with known issues...",
      "severity": "critical",
      "frequency": "10-15% of traces",
      "trace_urls": [
        "https://www.lmnr.ai/traces/a0dbd0c7-116d-776b-9c4b-c7f5f4d0a97e",
        "https://www.lmnr.ai/traces/5de277ff-38f2-e173-4b03-c7332301ea58"
      ]
    }
  ],
  "recommendations": [
    {
      "title": "Enforce Logic Verification Over Style",
      "description": "Modify the prompt to separate style from logic analysis...",
      "addresses": ["Premature Approval of Functional Defects"],
      "priority": "high"
    }
  ],
  "metrics": {
    "total_signals": 50,
    "issue_rate": "30%",
    "key_statistics": [...]
  },
  "strengths": [
    {"title": "Security Analysis", "description": "..."}
  ],
  "summary": "Executive summary of critical improvements needed..."
}
```

### Example Markdown Output

```markdown
# Agent Improvement Report

**Signal:** `pr review suggestion and analysis`

## Executive Summary

The AI agent demonstrates strong security awareness but suffers from...

## Issues Requiring Attention

### 1. [CRITICAL] Premature Approval of Functional Defects

The AI approves code with known issues...

**Frequency:** 10-15% of traces

**Example traces:**
- https://www.lmnr.ai/traces/a0dbd0c7-116d-776b-9c4b-c7f5f4d0a97e
- https://www.lmnr.ai/traces/5de277ff-38f2-e173-4b03-c7332301ea58

## Recommended Fixes

### 1. [HIGH PRIORITY] Enforce Logic Verification Over Style

Modify the prompt to separate style from logic analysis...

*Fixes: Premature Approval of Functional Defects*
```

## Custom Prompt Templates

Create a Jinja2 template (`.j2`) with access to:

| Variable | Type | Description |
|----------|------|-------------|
| `signals` | `list[dict]` | List of parsed signal objects |
| `num_signals` | `int` | Number of signals |
| `signal_name` | `str` | Name of the signal |

Each signal object contains:
- `trace_url`: Full URL to view the trace in Laminar
- `trace_id`: Trace UUID
- `timestamp`: When the signal was created
- `payload`: Parsed payload as dict
- `payload_json`: Formatted JSON string
- All payload fields flattened to top level

## Laminar SQL API Reference

The script uses Laminar's SQL API at `/v1/sql/query`. Key tables:

- `signal_events`: Signal events with trace_id and payload
- `traces`: Trace-level aggregates

See [Laminar SQL Editor documentation](https://docs.laminar.sh/platform/sql-editor) for details.
