# riskbench_core/agents/base.py

from abc import ABC, abstractmethod
from riskbench_core.taskspec import TaskSpec
from typing import Any

class BaseAgent(ABC):
    """
    All Agents must subclass this and implement act().
    """

    def __init__(self, spec: TaskSpec):
        self.spec = spec

    @abstractmethod
    def act(self, obs: Any) -> Any:
        """
        Given an observation, return an action.
        """
        ...
