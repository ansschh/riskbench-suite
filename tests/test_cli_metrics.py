# tests/test_cli_metrics.py

import json
from pathlib import Path
from click.testing import CliRunner

from riskbench_core.cli import cli

def write_log(path: Path, events: list):
    with open(path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

def test_metrics_cli(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    events = [
        {"step":0, "obs":{}, "action":None, "loss":0, "budget":0},
        {"step":1, "obs":{}, "action":None, "outcome":"success", "total_loss":2.5}
    ]
    write_log(logs/"x.jsonl", events)
    write_log(logs/"y.jsonl", events)

    runner = CliRunner()
    out_md   = tmp_path / "report.md"
    out_png  = tmp_path / "tradeoff.png"

    res = runner.invoke(cli, [
        "metrics",
        "--logs", str(logs/"*.jsonl"),
        "--alpha", "0.5",
        "--out", str(out_md),
        "--plot", str(out_png)
    ])
    assert res.exit_code == 0
    assert out_md.exists()
    assert out_png.exists()

    content = out_md.read_text(encoding="utf-8")
    assert "SuccessRate" in content and "|" in content
