from dataclasses import dataclass
from typing import Optional
from .states import SystemState

@dataclass
class Feedback:
    stability: float
    efficiency: float
    error: Optional[str] = None

@dataclass
class StepResult:
    previous_state: SystemState
    current_state: SystemState
    valid: bool
    consecutive_failures: int
