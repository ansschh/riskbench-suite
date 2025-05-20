# riskbench_core/envs/base.py

from abc import ABC, abstractmethod
from riskbench_core.taskspec import TaskSpec
from typing import Any, Tuple, Dict

class BaseEnvironment(ABC):
    """
    All Environments must subclass this and implement reset/step.
    """

    def __init__(self, spec: TaskSpec):
        self.spec = spec

    @abstractmethod
    def reset(self) -> Any:
        """
        Reset to initial state. Return initial observation.
        """
        ...

    @abstractmethod
    def step(self, action: Any) -> Tuple[Any, float, bool, Dict[str, Any]]:
        """
        Execute `action`. Return
          - next_obs: Any
          - loss: float
          - done: bool
          - info: dict (e.g. budget state)
        """
        ...
