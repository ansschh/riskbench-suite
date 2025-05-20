# tests/test_simulator.py

import os
import json
import yaml
from pathlib import Path
import pytest

from riskbench_core.simulator import simulate_directory
from riskbench_core.taskspec import TaskSpec

# Minimal valid spec dict
BASE_SPEC = {
    "id": "foo_task",
    "instruction": "Perform action.",
    "init_state": {"url": "https://example.com", "cookies": []},
    "tools": ["click", "navigate"],
    "evaluation": {"success_if": {"css": "#ok", "count_ge": 1}},
    "risk_annotations": []
}

def write_yaml_spec(path: Path, spec: dict):
    path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")

def test_simulate_creates_expected_files(tmp_path):
    # Setup tasks dir with one spec
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    spec_file = tasks_dir / "foo.yaml"
    write_yaml_spec(spec_file, BASE_SPEC)

    out_dir = tmp_path / "out"
    created = simulate_directory(str(tasks_dir), episodes=3, p_fail=0.5, extra_cost=50.0, out_dir=str(out_dir))

    # Expect exactly 3 files
    assert len(created) == 3
    for fp in created:
        assert os.path.isfile(fp)
        lines = Path(fp).read_text(encoding="utf-8").splitlines()
        # Two lines per file
        assert len(lines) == 2

        e0 = json.loads(lines[0])
        e1 = json.loads(lines[1])

        # Check keys in first event
        assert e0["step"] == 0
        assert "loss" in e0 and "budget" in e0

        # Check keys in second event
        assert e1["step"] == 1
        assert "outcome" in e1 and "total_loss" in e1

def test_simulate_no_specs(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    out_dir = tmp_path / "out"
    created = simulate_directory(str(empty), episodes=5, p_fail=0.1, extra_cost=10.0, out_dir=str(out_dir))
    # No specs → no files
    assert created == []
    # But out_dir was created
    assert out_dir.exists()
    assert list(out_dir.iterdir()) == []
