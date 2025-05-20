# tests/test_monitors.py

import pytest
from riskbench_core.monitors import BudgetMonitor, CVaRMonitor, MonitorBreachException


def test_budget_monitor_allows_under_limit():
    m = BudgetMonitor(spec=None, budget_limit=10.0)
    # budgets at or below limit do not raise
    for b in [0, 5, 10]:
        m.on_event({"budget": b})


def test_budget_monitor_raises_over_limit():
    m = BudgetMonitor(spec=None, budget_limit=10.0)
    with pytest.raises(MonitorBreachException) as exc:
        m.on_event({"budget": 10.01})
    assert "exceeded limit 10.00" in str(exc.value)


def test_cvar_monitor_accumulates_without_limit():
    m = CVaRMonitor(spec=None, alpha=0.8, cvar_limit=None)
    # just record; never raises
    for loss in [1.0, 2.0, 3.0, 4.0]:
        m.on_event({"loss": loss})
    assert m.losses == [1.0, 2.0, 3.0, 4.0]


def test_cvar_monitor_enforces_limit():
    # For alpha=0.5 on losses [1,2,4], CVaR = average of top 50% = avg([2,4]) = 3.0
    m = CVaRMonitor(spec=None, alpha=0.5, cvar_limit=2.5)
    m.on_event({"loss": 1.0})
    m.on_event({"loss": 2.0})
    # Still below limit: tail=[2, ...] avg=?
    m.on_event({"loss": 4.0})
    # At this point CVaR = 3.0 > 2.5 → breach
    with pytest.raises(MonitorBreachException) as exc:
        m.on_event({"loss": 0.0})  # trigger check again
    assert "CVaR@0.50 = 3.00 exceeded limit 2.50" in str(exc.value)


def test_invalid_alpha_raises():
    with pytest.raises(ValueError):
        CVaRMonitor(spec=None, alpha=1.0, cvar_limit=1.0)
    with pytest.raises(ValueError):
        CVaRMonitor(spec=None, alpha=0.0, cvar_limit=1.0)
