from collections import defaultdict, deque
from datetime import datetime, timedelta

class FlapProtector:
    def __init__(self, threshold=2, window_min=5):
        self.threshold = threshold
        self.window_min = window_min
        self.store = defaultdict(lambda: deque())

    def add_failure(self, name):
        now = datetime.now()
        dq = self.store[name]
        dq.append(now)
        cutoff = now - timedelta(minutes=self.window_min)
        while dq and dq[0] < cutoff:
            dq.popleft()
        return len(dq)

    def should_restart(self, name):
        return self.add_failure(name) >= self.threshold

    def reset(self, name):
        if name in self.store:
            self.store[name].clear()
