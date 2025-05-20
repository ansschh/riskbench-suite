# riskbench_core/simulator.py

import os
import glob
import json
import random
from typing import List, Dict, Any
from riskbench_core.taskspec import TaskSpec


def simulate_run(episode_index: int, p_fail: float, extra_cost: float) -> List[Dict[str, Any]]:
    """
    Simulate a single run:
      - Step 0: no loss.
      - Step 1: success (loss=0) or failure (loss=extra_cost) based on p_fail.
    Returns list of event dicts.
    """
    # Step 0: initial state
    events: List[Dict[str, Any]] = [
        {
            "step": 0,
            "obs": {},
            "action": None,
            "loss": 0.0,
            "budget": 0.0
        }
    ]

    # Decide failure
    if random.random() < p_fail:
        loss = extra_cost
        outcome = "failure"
    else:
        loss = 0.0
        outcome = "success"

    # Step 1: terminal event
    events.append({
        "step": 1,
        "obs": {},
        "action": None,
        "outcome": outcome,
        "total_loss": loss
    })

    return events


def simulate_directory(
    dir_path: str,
    episodes: int,
    p_fail: float,
    extra_cost: float,
    out_dir: str
) -> List[str]:
    """
    For each TaskSpec YAML under dir_path, run `episodes` simulations
    and write JSONL files into out_dir. Returns list of generated file paths.
    """
    # Find all YAML specs
    pattern = os.path.join(dir_path.rstrip("/"), "**", "*.yaml")
    spec_paths = glob.glob(pattern, recursive=True)

    os.makedirs(out_dir, exist_ok=True)
    created_files: List[str] = []

    for spec_path in spec_paths:
        spec = TaskSpec.load(spec_path)  # validate + load
        for i in range(episodes):
            events = simulate_run(i, p_fail, extra_cost)
            filename = f"{spec.id}_{i}.jsonl"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            created_files.append(filepath)

    return created_files
