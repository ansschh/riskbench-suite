# riskbench_core/dashboard.py

import os
import glob
import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from riskbench_core.riskmetrics import RiskReport

# Read logs dir from env var set by CLI
LOGS_DIR = os.getenv("RISKBENCH_LOGS_DIR", "logs")

app = FastAPI()

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/logs")
def list_logs(search: str | None = None) -> List[str]:
    pattern = os.path.join(LOGS_DIR, "*.jsonl")
    files = [os.path.basename(p) for p in sorted(glob.glob(pattern))]
    if search:
        search = search.lower()
        files = [f for f in files if search in f.lower()]
    return files

@app.get("/api/metrics")
def get_metrics(files: str | None = None, alpha: float = 0.9):
    # Build list of file paths
    if files:
        names = files.split(",")
        paths = [os.path.join(LOGS_DIR, n) for n in names]
    else:
        paths = glob.glob(os.path.join(LOGS_DIR, "*.jsonl"))
    # Filter to existing
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        raise HTTPException(404, "No matching log files found")

    # Compute summary across all logs
    # Use RiskReport.from_logs on the directory, but we want only these files:
    report = RiskReport.from_logs(os.path.join(LOGS_DIR, "*.jsonl"))
    summary = report.summary_table(alpha).iloc[0].to_dict()

    # Build per-run scatter data
    runs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            lines = f.read().splitlines()
        last = json.loads(lines[-1]) if lines else {}
        runs.append({
            "run": os.path.basename(p),
            "total_loss": float(last.get("total_loss", 0.0)),
            "success": 1.0 if last.get("outcome") == "success" else 0.0
        })

    return {"summary": summary, "runs": runs}

@app.get("/api/log/{filename}")
def get_log(filename: str):
    path = os.path.join(LOGS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "Log not found")
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            events.append(json.loads(line))
    return {"events": events}
