# tests/test_riskmetrics.py

import json
from pathlib import Path
import pytest

from riskbench_core.riskmetrics import RiskReport

def write_log(path: Path, events: list):
    with open(path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

@pytest.fixture
def sample_logs(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    # Run A: success, loss=5
    events_a = [
        {"step":0, "obs":{}, "action":None, "loss":0, "budget":0},
        {"step":1, "obs":{}, "action":None, "outcome":"success", "total_loss":5.0}
    ]
    # Run B: failure, loss=15
    events_b = [
        {"step":0, "obs":{}, "action":None, "loss":0, "budget":0},
        {"step":1, "obs":{}, "action":None, "outcome":"failure", "total_loss":15.0}
    ]
    write_log(logs/"a.jsonl", events_a)
    write_log(logs/"b.jsonl", events_b)
    return str(logs/"*.jsonl")

def test_summary_table(sample_logs):
    report = RiskReport.from_logs(sample_logs)
    df = report.summary_table(alpha=0.5)
    # SuccessRate = 1/2 = 0.5
    assert pytest.approx(0.5) == df["SuccessRate"].iloc[0]
    # EDL = (5 + 15)/2 = 10
    assert pytest.approx(10.0) == df["EDL"].iloc[0]
    # CVaR@50: losses=[5,15], alpha=0.5 → idx=ceil(0.5*2)-1=0 → tail=[5,15], mean=10
    assert pytest.approx(10.0) == df["CVaR@50"].iloc[0]
    # BreachRate = 1 - 0.5 = 0.5
    assert pytest.approx(0.5) == df["BreachRate"].iloc[0]

def test_plot_tradeoff_creates_png(sample_logs, tmp_path):
    report = RiskReport.from_logs(sample_logs)
    out_png = tmp_path / "tradeoff.png"
    report.plot_tradeoff(output_path=str(out_png))
    assert out_png.exists()
