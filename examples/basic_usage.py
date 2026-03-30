from acce import ACCEngine, Feedback

engine = ACCEngine()

feedbacks = [
    Feedback(stability=0.85, efficiency=0.80),
    Feedback(stability=0.60, efficiency=0.70),
    Feedback(stability=0.90, efficiency=0.88),
]

for f in feedbacks:
    result = engine.step(f)
    print(result)
