import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from acce import ACCEngine, Feedback, SystemState


def on_buffer(feedback: Feedback):
    print("HOOK: Entered BUFFER - recovery mode triggered")


def on_catalyze(feedback: Feedback):
    print("HOOK: Entered CATALYZE - optimization mode triggered")


def on_control(feedback: Feedback):
    print("HOOK: Entered CONTROL - clean termination achieved")


engine = ACCEngine()

engine.register_hook(SystemState.BUFFER, on_buffer)
engine.register_hook(SystemState.CATALYZE, on_catalyze)
engine.register_hook(SystemState.CONTROL, on_control)

feedbacks = [
    Feedback(stability=0.85, efficiency=0.80),
    Feedback(stability=0.50, efficiency=0.90),
    Feedback(stability=0.90, efficiency=0.60),
    Feedback(stability=0.92, efficiency=0.90),
    Feedback(stability=0.95, efficiency=0.93),
    Feedback(stability=0.98, efficiency=0.96),
]

for f in feedbacks:
    result = engine.step(f)
    print(
        f"{result.previous_state.name} -> {result.current_state.name} | "
        f"valid={result.valid} | "
        f"failures={result.consecutive_failures} | "
        f"stable_cycles={result.consecutive_stable_cycles} | "
        f"avg_stability={result.avg_stability} | "
        f"avg_efficiency={result.avg_efficiency} | "
        f"oscillating={result.oscillating} | "
        f"reason={result.reason}"
    )
