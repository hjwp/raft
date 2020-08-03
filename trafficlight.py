import time
from dataclasses import dataclass
from itertools import cycle

GREEN = '🟢⚫⚫'
AMBER = '⚫🟡⚫'
RED = '⚫⚫🔴'

STATE_CYCLE = (
    (GREEN, RED, 30),
    (AMBER, RED, 5),
    (RED, GREEN, 60),
    (RED, AMBER, 5),
    (GREEN, RED, 30),
)


@dataclass
class TrafficLight:
    ns: str
    ew: str
    time_til_next: int

    def __init__(self) -> None:
        self._cycle = cycle(STATE_CYCLE)
        self.next()

    def next(self) -> None:
        self._last_cycle_time = time.time()
        self.ns, self.ew, self.time_til_next = next(self._cycle)

    def tick(self) -> None:
        self.time_til_next -= 1

    def push_button(self) -> None:
        if self.ns == RED and self.ew == GREEN:
            pass
