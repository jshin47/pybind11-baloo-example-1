import datetime
import time

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

class PythonBasedOrderBookSnapshot:

    def __init__(self, save_messages = True):
        self.save_messages = save_messages
        self.deltas = { }
        self.asks = { }
        self.bids = { }

    def apply(self, delta):
        if self.save_messages:
            self.deltas[delta.timestamp] = delta
        which_map = self.asks if delta.direction == OrderDirection.Ask else self.bids
        if delta.quantity == 0:
            which_map.pop(delta.price, None)
        else:
            which_map[delta.price] = delta.quantity

    def apply_fast(self, change):
        
        side, price, quant = change
        side = self.asks if side == 1 else self.bids

        if quant == 0:
            side.pop(price)
        else:
            side[price] = quant
    # Terribly inefficient, but just wanted to make sure it was very clear what this is doing - and use a different algorithm from the cpp implementation.
    # TODO: Add another implementation of this so that we can verify that it does what we think it does.
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
    # TODO: Add another implementation of this so that we can verify that it does what we think it does.
    def apply_and_bucket(self, deltas, time_buckets, bins, ignore_deltas_before_beginning_of_first_bin = True, calculate_bid_ask_spread_features = True):
        if ignore_deltas_before_beginning_of_first_bin == False:
            deltas_before_first_bin = list(filter(lambda delta: delta.timestamp < time_buckets[0], deltas))
            for delta in deltas_before_first_bin:
                apply(delta)

        deltas = list(filter(lambda delta: delta.timestamp >= time_buckets[0], deltas))
        output = []

        for i in range(0, len(time_buckets) - 1):
            left_pt = time_buckets[i]
            rite_pt = time_buckets[i + 1]
            deltas_for_time_pt = list(filter(lambda delta: delta.timestamp >= left_pt and delta.timestamp < rite_pt, deltas))
            for delta in deltas_for_time_pt:
                self.apply(delta)
            output_for_time_pt = self.calculate_bid_ask_differential_bins(bins)
            if (calculate_bid_ask_spread_features):
                best_ask_price = min(self.asks, key=float) if (len(self.asks) > 0) else 0
                best_ask_quantity = self.asks[best_ask_price] if (len(self.asks) > 0) else 0
                best_bid_price = max(self.bids, key=float) if (len(self.bids) > 0) else 0
                best_bid_quantity = self.bids[best_bid_price] if (len(self.bids) > 0) else 0
                bid_ask_spread = best_ask_price - best_bid_price if (best_ask_price is not None and best_bid_price is not None) else 0
                output_for_time_pt.append(best_bid_price)
                output_for_time_pt.append(best_ask_price)
                output_for_time_pt.append(best_bid_quantity)
                output_for_time_pt.append(best_ask_quantity)

            output.append(output_for_time_pt)

        return output


