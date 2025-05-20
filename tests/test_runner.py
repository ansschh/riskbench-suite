# tests/test_runner.py

import os
import json
import yaml
from pathlib import Path
import tempfile
import pytest

from riskbench_core.runner import BenchmarkRunner
from riskbench_core.taskspec import TaskSpec
from riskbench_core.envs.base import BaseEnvironment
from riskbench_core.agents.base import BaseAgent

# 6.4.1.1 Minimal spec dict
BASE_SPEC = {
    "id": "foo_task",
    "instruction": "Test runner.",
    "init_state": {"url": "https://example.com", "cookies": []},
    "tools": ["click"],
    "evaluation": {"success_if": {"css": "#ok", "count_ge": 1}},
    "risk_annotations": []
}

# 6.4.1.2 Write YAML helper
def write_spec(path: Path, spec: dict):
    path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")

# 6.4.1.3 Dummy implementations
class DummyEnv(BaseEnvironment):
    def reset(self):
        return {"state": 0}
    def step(self, action):
        # one‐step env: always succeed with loss = state + 1
        state = action if isinstance(action, int) else 0
        return {"state": state}, float(state), True, {"budget": state}

class DummyAgent(BaseAgent):
    def act(self, obs):
        # increment state
        return obs.get("state", 0) + 1

class DummyMonitor:
    def __init__(self, spec):
        self.events = []
    def on_event(self, event):
        self.events.append(event)

def test_runner_direct(tmp_path):
    # ---- setup
    tasks = tmp_path / "tasks"; tasks.mkdir()
    spec_file = tasks / "foo.yaml"; write_spec(spec_file, BASE_SPEC)

    # ---- run
    runner = BenchmarkRunner(
        env_cls=DummyEnv,
        agent_classes=[DummyAgent],
        risk_monitor_classes=[DummyMonitor],
        max_steps=5
    )
    results = runner.run(str(tasks / "*.yaml"), parallel=1)

    # ---- assertions
    assert len(results) == 1
    spec_id, agent_name, logs = results[0]
    assert spec_id == "foo_task"
    assert agent_name == "DummyAgent"
    # initial event + 1 step + final outcome = 3 events
    assert len(logs) == 3
    assert logs[0]["step"] == 0 and logs[-1]["total_loss"] == logs[1]["loss"]

def test_run_cli(tmp_path, monkeypatch):
    # write spec
    tasks = tmp_path / "tasks"; tasks.mkdir()
    spec_file = tasks / "foo.yaml"
    write_spec(spec_file, BASE_SPEC)

    # register DummyEnv/Agent/Monitor as plugins
    from riskbench_core.plugins import register_plugin
    register_plugin("riskbench.envs", "DummyEnv", DummyEnv)
    register_plugin("riskbench.agents", "DummyAgent", DummyAgent)
    register_plugin("riskbench.monitors", "DummyMonitor", DummyMonitor)

    # run CLI
    out = tmp_path / "logs"
    cmd = [
        "run",
        "--tasks", str(tasks / "*.yaml"),
        "--env", "DummyEnv",
        "--agents", "DummyAgent",
        "--monitors", "DummyMonitor",
        "--out-dir", str(out)
    ]
    # invoke via click runner
    from click.testing import CliRunner
    from riskbench_core.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, cmd)
    print("CLI Output:", res.output)
    print("CLI Exit Code:", res.exit_code)
    assert res.exit_code == 0
    # check output directory
    files = list(out.iterdir())
    print("Output files:", files)
    assert len(files) == 1
    data = [json.loads(line) for line in files[0].read_text().splitlines()]
    print("Log data:", data)
    assert any("total_loss" in ev for ev in data)
