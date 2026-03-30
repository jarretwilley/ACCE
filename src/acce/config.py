from dataclasses import dataclass


@dataclass
class ACCEConfig:
    stability_threshold: float = 0.80
    efficiency_threshold: float = 0.75

    low_stability_trigger: float = 0.60
    low_efficiency_trigger: float = 0.70

    stability_target: float = 0.88
    stable_cycles_required: int = 2

    max_consecutive_failures: int = 5

    history_window: int = 5
    oscillation_window: int = 6
