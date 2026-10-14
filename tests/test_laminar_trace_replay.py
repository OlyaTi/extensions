import importlib.util
import io
import urllib.error
from pathlib import Path
from types import SimpleNamespace

import pytest

path = Path(__file__).parents[1] / "utils/analysis/laminar_signals/replay.py"
spec = importlib.util.spec_from_file_location("trace_replay", path)
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def test_credentials_are_removed_from_nested_tool_output():
    credential = "example-credential-without-a-recognizable-prefix"
    result = replay.redact(
        {
            "output": f"Authorization: Bearer {credential}; contact person@example.com",
            "nested": [{"api_key": credential}, {"text": credential}],
            "automation.run_id": "run-123",
        },
        (credential,),
    )
    assert credential not in str(result)
    assert "person@example.com" not in str(result)
    assert result["automation.run_id"] == "run-123"


@pytest.mark.parametrize("span_ids", [[], ["unknown"], ["recorded", "unknown"]])
def test_findings_cannot_cite_missing_evidence(span_ids):
    sample = {"session_id": "session", "spans": [{"span_id": "recorded"}]}
    result = {"findings": [{"span_ids": span_ids, "description": "Failure"}]}
    with pytest.raises(ValueError, match="spans"):
        replay.validate_findings(result, sample)


def test_findings_preserve_evidence_references():
    sample = {"session_id": "session", "spans": [{"span_id": "recorded"}]}
    result = {"findings": [{"span_ids": ["recorded"], "description": "Failure"}]}
    findings = replay.validate_findings(result, sample)
    assert findings[0]["span_ids"] == ["recorded"]
    assert findings[0]["id"]


def test_http_errors_do_not_echo_provider_credentials(monkeypatch):
    key = "example-sensitive-provider-credential"

    def fail(*args, **kwargs):
        raise urllib.error.HTTPError(
            "https://example.com", 401, "Rejected", {}, io.BytesIO(key.encode())
        )

    monkeypatch.setattr(replay.urllib.request, "urlopen", fail)
    with pytest.raises(RuntimeError) as error:
        replay.post_json("https://example.com", key, {}, 1)
    assert "401" in str(error.value)
    assert key not in str(error.value)


def test_oversized_samples_make_no_inference_requests(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text('{"samples": [{"spans": ["oversized evidence"]}]}')
    args = SimpleNamespace(input=snapshot, limit=1, max_input_chars=1)
    calls = []
    monkeypatch.setattr(replay, "judge", lambda *args: calls.append(args))
    with pytest.raises(ValueError, match="input limit"):
        replay.analyze(args)
    assert calls == []
