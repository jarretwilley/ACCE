from enum import Enum, auto


class SystemState(Enum):
    INIT = auto()
    STRUCTURE = auto()
    BOND = auto()
    BUFFER = auto()
    CATALYZE = auto()
    CONTROL = auto()
