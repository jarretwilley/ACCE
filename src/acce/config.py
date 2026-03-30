from dataclasses import dataclass

@dataclass
class ACCEConfig:
    stability_threshold: float = 0.80
    efficiency_threshold: float = 0.75
    stability_target: float = 0.88
    max_consecutive_failures: int = 5
    stabilization_window: int = 8
