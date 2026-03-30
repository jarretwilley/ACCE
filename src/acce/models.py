from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .states import SystemState


@dataclass
class Feedback:
    stability: float
    efficiency: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    previous_state: SystemState
    current_state: SystemState
    valid: bool
    consecutive_failures: int
    consecutive_stable_cycles: int
    avg_stability: float
    avg_efficiency: float
    oscillating: bool
    reason: str
