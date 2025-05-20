# tests/test_cli.py
import os
from pathlib import Path
from click.testing import CliRunner
from riskbench_core.cli import cli

def test_init_creates_example(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["init"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "✔  Created tasks/example_task.yaml" in result.output
    assert Path(tmp_path / "tasks" / "example_task.yaml").exists()

def test_validate_success(tmp_path, monkeypatch):
    yaml = tmp_path / "t.yaml"
    yaml.write_text("""
id: mytask
instruction: x
init_state:
  url: https://example.com
  cookies: []
tools: [click]
evaluation:
  success_if:
    css: "#a"
    count_ge: 1
""", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(yaml)], catch_exceptions=False)
    assert result.exit_code == 0
    assert "✅" in result.output

def test_validate_fail(tmp_path, monkeypatch):
    bad = tmp_path / "bad.yaml"
    bad.write_text("""
id: "!bad id"
instruction: ""
tools: []
evaluation:
  success_if:
    css: ""
    count_ge: null
""", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(bad)], catch_exceptions=False)
    assert result.exit_code == 1
    assert "❌" in result.output
