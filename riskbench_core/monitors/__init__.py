# riskbench_core/monitors/__init__.py

from typing import Any, Dict, List
import math

__all__ = ['MonitorBreachException', 'BudgetMonitor', 'CVaRMonitor', 
           'BudgetMonitor50', 'BudgetMonitor100', 'CVaRMonitor90', 'CVaRMonitor95']


class MonitorBreachException(Exception):
    """
    Thrown by a monitor to signal that a safety condition was violated.
    """
    pass


class BudgetMonitor:
    """
    Enforce an upper bound on the 'budget' field in events.
    """

    def __init__(self, spec: Any, budget_limit: float):
        self.budget_limit = float(budget_limit)

    def on_event(self, event: Dict[str, Any]) -> None:
        budget = float(event.get("budget", 0.0))
        if budget > self.budget_limit:
            raise MonitorBreachException(
                f"BudgetMonitor: budget {budget:.2f} exceeded limit {self.budget_limit:.2f}"
            )


class CVaRMonitor:
    """
    Track episode losses and (optionally) enforce a CVaR threshold.
    If `cvar_limit` is None, it simply accumulates losses for post‐hoc analysis.
    """

    def __init__(self, spec: Any, alpha: float, cvar_limit: float | None = None):
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be in (0,1)")
        self.alpha = float(alpha)
        self.cvar_limit = None if cvar_limit is None else float(cvar_limit)
        self.losses: List[float] = []

    def on_event(self, event: Dict[str, Any]) -> None:
        # Record any per-step loss
        if "loss" in event:
            loss = float(event["loss"])
            if loss != 0.0:
                self.losses.append(loss)
                # Don't check limit when recording a non-zero loss
                return

        # If there's no enforcement threshold, do nothing further
        if self.cvar_limit is None or not self.losses:
            return

        # Only check limit on non-loss events or zero-loss events
        # This ensures we have all losses before checking
        sorted_losses = sorted(self.losses)
        n = len(sorted_losses)
        # index of the first loss in the worst (1-alpha) tail
        idx = min(max(int(math.ceil(self.alpha * n)) - 1, 0), n - 1)
        var = sorted_losses[idx]
        tail = sorted_losses[idx:]
        cvar = sum(tail) / len(tail)

        if cvar > self.cvar_limit:
            raise MonitorBreachException(
                f"CVaRMonitor: CVaR@{self.alpha:.2f} = {cvar:.2f} exceeded limit {self.cvar_limit:.2f}"
            )


# --- Factory functions for common presets ---

def BudgetMonitor50(spec):
    return BudgetMonitor(spec, budget_limit=50.0)

def BudgetMonitor100(spec):
    return BudgetMonitor(spec, budget_limit=100.0)

def CVaRMonitor90(spec):
    # alpha=0.9, no enforcement limit (just logging)
    return CVaRMonitor(spec, alpha=0.9, cvar_limit=None)

def CVaRMonitor95(spec):
    # alpha=0.95, no enforcement limit
    return CVaRMonitor(spec, alpha=0.95, cvar_limit=None)
