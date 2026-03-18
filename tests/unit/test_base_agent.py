"""Test BasePolsiaAgent.call_claude() — subprocess mock."""
import json
import os
import pytest
from unittest.mock import patch

from app.agents.base_agent import BasePolsiaAgent


class ConcreteAgent(BasePolsiaAgent):
    agent_type = "test"

    def run(self, task, context):
        return {"summary": "test"}


def test_call_claude_returns_mock_when_env_set(monkeypatch):
    monkeypatch.setenv("CLAUDE_CLI_MOCK", "true")
    monkeypatch.setenv("CLAUDE_CLI_MOCK_RESPONSE", json.dumps({"result": "hello from mock"}))

    agent = ConcreteAgent()
    result = agent.call_claude("test prompt")

    assert result == "hello from mock"


def test_call_claude_does_not_invoke_subprocess_in_mock_mode(monkeypatch):
    monkeypatch.setenv("CLAUDE_CLI_MOCK", "true")
    agent = ConcreteAgent()

    with patch("subprocess.run") as mock_run:
        agent.call_claude("test prompt")
        mock_run.assert_not_called()


def test_call_claude_json_parses_result(monkeypatch):
    monkeypatch.setenv("CLAUDE_CLI_MOCK", "true")
    monkeypatch.setenv(
        "CLAUDE_CLI_MOCK_RESPONSE",
        json.dumps({"result": '{"key": "value", "number": 42}'}),
    )

    agent = ConcreteAgent()
    result = agent.call_claude_json("test")
    assert result == {"key": "value", "number": 42}


def test_timed_run_adds_duration():
    agent = ConcreteAgent()
    result = agent.timed_run({"title": "test"}, {})
    assert "duration_secs" in result
    assert isinstance(result["duration_secs"], float)
