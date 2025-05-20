# riskbench_core/riskmetrics.py

import glob
import json
import math
import os
from typing import List, Dict

import pandas as pd
import matplotlib.pyplot as plt


class RiskReport:
    """
    Compute summary risk metrics and trade-off plots from JSONL logs.
    """

    def __init__(self, records: List[Dict]):
        # records: one dict per run with keys 'outcome', 'total_loss', 'run'
        self.df = pd.DataFrame(records)

    @classmethod
    def from_logs(cls, pattern: str) -> "RiskReport":
        """
        Load all JSONL files matching `pattern` (glob).
        Each file is one run; take its LAST event for metrics.
        """
        filepaths = sorted(glob.glob(pattern, recursive=True))
        records: List[Dict] = []
        for path in filepaths:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            if not lines:
                continue
            last = json.loads(lines[-1])
            outcome = last.get("outcome", "failure")
            total_loss = float(last.get("total_loss", 0.0))
            records.append({
                "run": os.path.basename(path),
                "outcome": outcome,
                "total_loss": total_loss
            })
        return cls(records)

    def summary_table(self, alpha: float = 0.9) -> pd.DataFrame:
        """
        Returns a one-row DataFrame with:
          - SuccessRate: fraction of runs with outcome=='success'
          - EDL: mean of total_loss
          - CVaR@{alpha*100}: mean of worst (1-alpha) tail losses
          - BreachRate: fraction of runs with outcome!='success'
        """
        total = len(self.df)
        # avoid division by zero
        if total == 0:
            return pd.DataFrame([{
                "SuccessRate": float("nan"),
                "EDL": float("nan"),
                f"CVaR@{int(alpha*100)}": float("nan"),
                "BreachRate": float("nan")
            }])

        # Success / breach
        success_mask = self.df["outcome"] == "success"
        success_rate = success_mask.sum() / total
        breach_rate = 1.0 - success_rate

        # Expected Dollar Loss (EDL)
        edl = self.df["total_loss"].mean()

        # Conditional Value at Risk (CVaR)
        losses = sorted(self.df["total_loss"].tolist())
        n = len(losses)
        # index of var: ceil(alpha*n)-1, clamped
        idx = max(min(math.ceil(alpha * n) - 1, n - 1), 0)
        tail = losses[idx:]
        cvar = sum(tail) / len(tail) if tail else 0.0

        return pd.DataFrame([{
            "SuccessRate": success_rate,
            "EDL": edl,
            f"CVaR@{int(alpha*100)}": cvar,
            "BreachRate": breach_rate
        }])

    def plot_tradeoff(
        self,
        metric: str = "success",
        risk: str = "total_loss",
        output_path: str = None
    ) -> None:
        """
        Scatter-plot: X = risk (e.g. total_loss), Y = metric (e.g. success=1/0).
        If output_path is given, saves a PNG; otherwise shows the plot.
        """
        # Prepare X
        if risk not in self.df.columns:
            raise ValueError(f"Risk field '{risk}' not in data")
        x = self.df[risk]

        # Prepare Y
        if metric == "success":
            y = self.df["outcome"].map(lambda o: 1.0 if o == "success" else 0.0)
        elif metric in self.df.columns:
            y = self.df[metric].astype(float)
        else:
            raise ValueError(f"Metric '{metric}' not found")

        plt.figure()
        plt.scatter(x, y)
        plt.xlabel(risk)
        plt.ylabel(metric)
        plt.tight_layout()

        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            plt.savefig(output_path)
            plt.close()
        else:
            plt.show()
