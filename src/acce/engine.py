from collections import deque
from typing import Deque, Callable, Dict, Optional

from .config import ACCEConfig
from .models import Feedback, StepResult
from .states import SystemState


StateHook = Callable[[Feedback], None]


class ACCEngine:
    def __init__(self, config: Optional[ACCEConfig] = None):
        self.config = config or ACCEConfig()
        self.current_state = SystemState.INIT

        self.history: Deque[Feedback] = deque(maxlen=max(50, self.config.history_window * 10))
        self.state_history: Deque[SystemState] = deque(maxlen=max(20, self.config.oscillation_window * 2))

        self.cycle = 0
        self.consecutive_failures = 0
        self.consecutive_stable_cycles = 0

        self.hooks: Dict[SystemState, StateHook] = {}

    def register_hook(self, state: SystemState, hook: StateHook) -> None:
        self.hooks[state] = hook

    def run_hook(self, state: SystemState, feedback: Feedback) -> None:
        hook = self.hooks.get(state)
        if hook:
            hook(feedback)

    def validate(self, feedback: Feedback) -> bool:
        return (
            feedback.stability >= self.config.stability_threshold
            and feedback.efficiency >= self.config.efficiency_threshold
            and not feedback.error
        )

    def get_recent_feedback(self) -> list[Feedback]:
        window = self.config.history_window
        if len(self.history) == 0:
            return []
        return list(self.history)[-window:]

    def average_metrics(self) -> tuple[float, float]:
        recent = self.get_recent_feedback()
        if not recent:
            return 0.0, 0.0

        avg_stability = sum(f.stability for f in recent) / len(recent)
        avg_efficiency = sum(f.efficiency for f in recent) / len(recent)
        return avg_stability, avg_efficiency

    def is_oscillating(self) -> bool:
        window = self.config.oscillation_window
        recent_states = list(self.state_history)[-window:]

        if len(recent_states) < window:
            return False

        unique_states = list(dict.fromkeys(recent_states))

        # crude thrash detection: bouncing between 2-3 states too much
        return len(set(recent_states)) <= 3 and len(unique_states) >= 2

    def classify(self, feedback: Feedback) -> str:
        if feedback.error:
            return "error"

        avg_stability, avg_efficiency = self.average_metrics()

        if feedback.stability < self.config.low_stability_trigger or avg_stability < self.config.low_stability_trigger:
            return "unstable"

        if feedback.efficiency < self.config.low_efficiency_trigger or avg_efficiency < self.config.low_efficiency_trigger:
            return "inefficient"

        if self.validate(feedback):
            return "stable"

        return "degraded"

    def next_state(self, feedback: Feedback) -> tuple[SystemState, str]:
        classification = self.classify(feedback)
        avg_stability, avg_efficiency = self.average_metrics()

        if self.is_oscillating():
            return SystemState.CONTROL, "oscillation_detected"

        if self.consecutive_failures >= self.config.max_consecutive_failures:
            return SystemState.CONTROL, "max_failures_reached"

        if (
            self.consecutive_stable_cycles >= self.config.stable_cycles_required
            and avg_stability >= self.config.stability_target
            and avg_efficiency >= self.config.efficiency_threshold
        ):
            return SystemState.CONTROL, "stability_target_achieved"

        if classification in ("error", "unstable"):
            return SystemState.BUFFER, classification

        if classification == "inefficient":
            return SystemState.CATALYZE, classification

        if self.current_state == SystemState.INIT:
            return SystemState.STRUCTURE, "normal_progression"

        if self.current_state == SystemState.STRUCTURE:
            return SystemState.BOND, "normal_progression"

        if self.current_state == SystemState.BOND:
            return SystemState.BOND, "continue_execution"

        if self.current_state == SystemState.BUFFER:
            return SystemState.STRUCTURE, "recovered_from_buffer"

        if self.current_state == SystemState.CATALYZE:
            return SystemState.BOND, "recovered_from_catalyze"

        return SystemState.CONTROL, "default_terminal"

    def step(self, feedback: Feedback) -> StepResult:
        previous_state = self.current_state
        self.cycle += 1
        self.history.append(feedback)

        valid = self.validate(feedback)

        if valid:
            self.consecutive_failures = 0
            self.consecutive_stable_cycles += 1
        else:
            self.consecutive_failures += 1
            self.consecutive_stable_cycles = 0

        next_state, reason = self.next_state(feedback)
        self.current_state = next_state
        self.state_history.append(self.current_state)

        self.run_hook(self.current_state, feedback)

        avg_stability, avg_efficiency = self.average_metrics()

        return StepResult(
            previous_state=previous_state,
            current_state=self.current_state,
            valid=valid,
            consecutive_failures=self.consecutive_failures,
            consecutive_stable_cycles=self.consecutive_stable_cycles,
            avg_stability=round(avg_stability, 3),
            avg_efficiency=round(avg_efficiency, 3),
            oscillating=self.is_oscillating(),
            reason=reason,
        )
