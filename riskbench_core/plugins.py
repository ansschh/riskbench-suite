# riskbench_core/plugins.py
from typing import Dict, Type, Any

_plugins = {
    "riskbench.envs": {},
    "riskbench.agents": {},
    "riskbench.monitors": {}
}

def register_plugin(group: str, name: str, plugin: Any):
    _plugins[group][name] = plugin

def get_envs() -> Dict[str, Type]:
    return _plugins["riskbench.envs"]

def get_agents() -> Dict[str, Type]:
    return _plugins["riskbench.agents"]

def get_monitors() -> Dict[str, Type]:
    return _plugins["riskbench.monitors"]
