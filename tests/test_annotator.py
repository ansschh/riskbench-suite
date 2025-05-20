# tests/test_annotator.py

import yaml
from pathlib import Path
import tempfile

import pytest
from riskbench_core.annotator import annotate_directory
from riskbench_core.taskspec import TaskSpec

# Minimal valid spec without any risk_annotations
BASE_SPEC = {
    "id": "foo_task",
    "instruction": "Do something safe.",
    "init_state": {"url": "https://example.com", "cookies": []},
    "tools": ["navigate","click"],
    "evaluation": {"success_if": {"css": "#ok", "count_ge": 1}},
    # no risk_annotations key at all
}

def write_spec(path: Path, spec_dict: dict):
    path.write_text(yaml.safe_dump(spec_dict, sort_keys=False), encoding="utf-8")

def load_annotations(path: Path):
    spec = TaskSpec.load(str(path))
    return {ann.label for ann in spec.risk_annotations}

def test_annotate_adds_defaults(tmp_path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    file1 = tasks_dir / "a.yaml"
    write_spec(file1, BASE_SPEC)

    updated = annotate_directory(str(tasks_dir))
    assert str(file1) in updated

    labels = load_annotations(file1)
    assert "destructive_click" in labels
    assert "insecure_nav" in labels

def test_annotate_idempotent(tmp_path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    file1 = tasks_dir / "a.yaml"
    # write once and annotate
    write_spec(file1, BASE_SPEC)
    annotate_directory(str(tasks_dir))
    # annotate again
    updated_again = annotate_directory(str(tasks_dir))
    assert updated_again == []  # no changes second time
