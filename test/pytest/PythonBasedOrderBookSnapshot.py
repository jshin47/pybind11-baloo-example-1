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

    def calculate_bid_ask_differential_bins(self, bins):
        bins_length = len(bins)
        bins_output = []

        for i in range(bins_length - 1):
            bin_price = bins[i]
            has_next_price = i < bins_length - 1
            next_price = bins[i + 1] if has_next_price else None
            total = 0
            for price, quantity in self.asks.items():
                if price >= bin_price and ((not has_next_price) or price < next_price):
                    total -= quantity
            for price, quantity in self.bids.items():
                if price >= bin_price and ((not has_next_price) or price < next_price):
                    total += quantity
            bins_output.append(total)
        
        return bins_output


