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

    # Terribly inefficient, but just wanted to make sure it was very clear what this is doing - and use a different algorithm from the cpp implementation.
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

    # Terribly inefficient, but just wanted to make sure it was very clear what this is doing - and use a different algorithm from the cpp implementation.
    def apply_and_bucket(self, deltas, time_buckets, bins):
        deltas = list(filter(lambda delta: delta.timestamp >= time_buckets[0], deltas))
        output = []

        for i in range(0, len(time_buckets) - 1):
            left_pt = time_buckets[i]
            rite_pt = time_buckets[i + 1]
            deltas_for_time_pt = list(filter(lambda delta: delta.timestamp >= left_pt and delta.timestamp < rite_pt, deltas))
            for delta in deltas_for_time_pt:
                self.apply(delta)
            output_for_time_pt = self.calculate_bid_ask_differential_bins(bins)
            output.append(output_for_time_pt)

        return output


