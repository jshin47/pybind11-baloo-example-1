import datetime
import time

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

class PythonBasedOrderBookSnapshot:

    def __init__(self, saveMessages = True):
        self.saveMessages = saveMessages
        self.deltas = { }
        self.asks = { }
        self.bids = { }

    def apply(self, delta):
        if self.saveMessages:
            self.deltas[delta.timestamp] = delta
        which_map = self.asks if delta.direction == OrderDirection.Ask else self.bids
        if delta.quantity == 0:
            which_map.pop(delta.price, None)
        else:
            which_map[delta.price] = delta.quantity

