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
)


@dataclass
class TrafficLight:
    ns: str
    ew: str
    time_til_next: int

    def __init__(self, current_time: float = None) -> None:
        if current_time is None:
            self.current_time = time.time()
        self._cycle = cycle(STATE_CYCLE)
        self.next()

    def next(self) -> None:
        self.ns, self.ew, self.time_til_next = next(self._cycle)

    def handle_clock_tick(self) -> None:
        self.time_til_next -= 1
        if self.time_til_next <= 0:
            self.next()

    def push_button(self) -> None:
        if self.ns == RED and self.ew == GREEN:
            self.time_til_next = max(0, self.time_til_next - 30)
