# riskbench_core/taskspec.py
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator, model_validator


class InitState(BaseModel):
    url: str = Field(..., pattern=r"^https?://[^\s/$.?#].[^\s]*$")
    cookies: List[Dict[str, Any]] = Field(default_factory=list)


class SuccessIf(BaseModel):
    css: str
    count_ge: int

    @model_validator(mode="before")
    def check_fields(cls, values):
        if isinstance(values, dict):
            css = values.get("css")
            count_ge = values.get("count_ge")
            if not css or count_ge is None:
                raise ValueError("Both 'css' and 'count_ge' must be set under 'success_if'")
            if not isinstance(css, str) or not isinstance(count_ge, int):
                raise ValueError("'css' must be a string and 'count_ge' must be an integer")
        return values


class Evaluation(BaseModel):
    success_if: SuccessIf


class RiskAnnotation(BaseModel):
    when: str
    cost: float
    label: str

    @field_validator("cost")
    def cost_non_negative(cls, v):
        if v < 0:
            raise ValueError("annotation 'cost' must be ≥ 0")
        return v


class TaskSpec(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    instruction: str = Field(..., min_length=1)
    init_state: InitState
    tools: List[str]

    @field_validator("tools")
    def validate_tools(cls, v):
        if not v:
            raise ValueError("tools list cannot be empty")
        return v
    evaluation: Evaluation
    risk_annotations: List[RiskAnnotation] = Field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> "TaskSpec":
        """Load a TaskSpec from a YAML file."""
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    raise ValueError("Empty YAML file")
                if not isinstance(data, dict):
                    raise ValueError("YAML content must be a dictionary")
            return cls.model_validate(data)
        except (yaml.YAMLError, OSError) as e:
            raise ValueError(f"Failed to load YAML: {e}")
        except Exception as e:
            raise ValueError(f"Failed to validate TaskSpec: {e}")

    def save(self, path: str) -> None:
        """
        Serialize TaskSpec to YAML, preserving field order.
        """
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(mode="json"), f, sort_keys=False)
