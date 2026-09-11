from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ObjectiveSpec:
    """
    Explicit optimization metadata.

    direction:
        "maximize" -> higher values are preferred
        "minimize" -> lower values are preferred
    """

    name: str
    direction: str
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Objective name cannot be empty.")

        if self.direction not in ("maximize", "minimize"):
            raise ValueError(
                "Objective direction must be 'maximize' or 'minimize'."
            )

        if self.priority < 0:
            raise ValueError("Objective priority cannot be negative.")


@dataclass(frozen=True)
class ObjectiveConfiguration:
    objectives: Tuple[ObjectiveSpec, ...]

    def __post_init__(self) -> None:
        names = [objective.name for objective in self.objectives]

        if len(names) != len(set(names)):
            raise ValueError("Objective names must be unique.")

    @property
    def ordered_objectives(self) -> Tuple[ObjectiveSpec, ...]:
        return tuple(
            sorted(
                self.objectives,
                key=lambda objective: objective.priority,
            )
        )

    def get(self, name: str) -> ObjectiveSpec | None:
        for objective in self.objectives:
            if objective.name == name:
                return objective

        return None
