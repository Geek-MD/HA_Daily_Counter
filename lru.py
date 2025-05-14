# lru.py - Mock for hassfest compatibility using functools.lru_cache

from collections import OrderedDict

class LRU(OrderedDict):
    """Simple LRU Cache replacement for hassfest using OrderedDict."""

    def __init__(self, size):
        self.size = size
        super().__init__()

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.size:
            oldest = next(iter(self))
            del self[oldest]
