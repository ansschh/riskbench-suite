# riskbench_core/runner.py

import os
import glob
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Type, Tuple, Any, Dict

from riskbench_core.taskspec import TaskSpec
from riskbench_core.envs.base import BaseEnvironment
from riskbench_core.agents.base import BaseAgent

class BenchmarkRunner:
    """
    Runs each Agent on each TaskSpec under a given Env, optionally with RiskMonitors.
    Produces a list of (spec_id, agent_name, logs) tuples.
    """

    def __init__(
        self,
        env_cls: Type[BaseEnvironment],
        agent_classes: List[Type[BaseAgent]],
        risk_monitor_classes: List[Type],
        max_steps: int = 100
    ):
        self.env_cls = env_cls
        self.agent_classes = agent_classes
        self.risk_monitor_classes = risk_monitor_classes
        self.max_steps = max_steps

    def _run_single(
        self, spec_path: str, agent_cls: Type[BaseAgent]
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        spec = TaskSpec.load(spec_path)
        env = self.env_cls(spec)
        agent = agent_cls(spec)
        monitors = [m(spec) for m in self.risk_monitor_classes]

        logs: List[Dict[str, Any]] = []
        # Step 0: initial state
        obs = env.reset()
        total_loss = 0.0
        budget = 0.0
        logs.append({
            "step": 0,
            "obs": obs,
            "action": None,
            "loss": 0.0,
            "budget": budget
        })

        step = 0
        done = False
        # Main loop
        while step < self.max_steps and not done:
            action = agent.act(obs)
            next_obs, loss, done, info = env.step(action)
            step += 1
            total_loss += loss
            budget = info.get("budget", budget)

            event = {
                "step": step,
                "obs": next_obs,
                "action": action,
                "loss": loss,
                "budget": budget
            }
            # Notify monitors
            for monitor in monitors:
                monitor.on_event(event)

            logs.append(event)
            obs = next_obs

        # Final outcome event
        logs.append({
            "step": step,
            "obs": obs,
            "action": None,
            "outcome": "success" if not done else "failure",
            "total_loss": total_loss
        })

        return spec.id, agent_cls.__name__, logs

    def run(
        self,
        task_pattern: str,
        parallel: int = 1
    ) -> List[Tuple[str, str, List[Dict[str, Any]]]]:
        """
        Discover all specs matching the glob `task_pattern`
        and run every agent on each one.
        Returns a list of (spec_id, agent_name, logs).
        """
        spec_paths = sorted(glob.glob(task_pattern, recursive=True))
        results: List[Tuple[str, str, List[Dict[str, Any]]]] = []

        if parallel > 1:
            with ThreadPoolExecutor(max_workers=parallel) as exe:
                futures = {
                    exe.submit(self._run_single, spec_path, agent_cls): (spec_path, agent_cls)
                    for spec_path in spec_paths
                    for agent_cls in self.agent_classes
                }
                for fut in as_completed(futures):
                    results.append(fut.result())
        else:
            for spec_path in spec_paths:
                for agent_cls in self.agent_classes:
                    results.append(self._run_single(spec_path, agent_cls))

        return results
