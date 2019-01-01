import unittest

import datetime
import time
import numpy as np

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

class BalooModuleTests(unittest.TestCase):

    def setUp(self):
        self._started_at = time.time()
    
    def tearDown(self):
        elapsed = time.time() - self._started_at

    def test_orderbook_delta_retains_values(self):
        delta1 = OrderBookDelta()
        timestamp = 1
        delta1.timestamp = timestamp
        self.assertEqual(delta1.timestamp, timestamp)
        delta1.price = 10.1
        self.assertEqual(delta1.price, 10.1)
        delta1.quantity = 40012
        self.assertEqual(delta1.quantity, 40012)
        delta1.direction = OrderDirection.Bid
        self.assertEqual(delta1.direction, OrderDirection.Bid)

    def test_orderbook_snapshot_applies_single(self):
        snapshot1 = OrderBookSnapshot()
        delta1 = OrderBookDelta()
        delta1.timestamp = 1
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        snapshot1.apply(delta1)
        delta2 = OrderBookDelta()
        delta2.timestamp = 1
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply(delta2)
        self.assertEqual(len(snapshot1.asks), 1)
        self.assertEqual(len(snapshot1.bids), 1)

    def test_orderbook_snapshot_applies_list(self):
        snapshot1 = OrderBookSnapshot()
        delta1 = OrderBookDelta()
        delta1.timestamp = 1
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        delta2 = OrderBookDelta()
        delta2.timestamp = 1
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply([delta1, delta2])
        self.assertEqual(len(snapshot1.asks), 1)
        self.assertEqual(len(snapshot1.bids), 1)

    def test_get_snapshot_at_point_in_time(self):
        snapshot1 = OrderBookSnapshot(save_messages = True)
        delta1 = OrderBookDelta()
        delta1.timestamp = 1
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        delta2 = OrderBookDelta()
        delta2.timestamp = 1
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply([delta1, delta2])
        snapshot2 = snapshot1.get_snapshot_at_point_in_time(delta1.timestamp)
        self.assertEqual(len(snapshot2.asks), 1)
        self.assertEqual(len(snapshot2.bids), 0)

    def test_apply_seems_quick_many_unique_keys(self):
        time_start = time.time()

        deltas = [OrderBookDelta(timestamp = (float)(i), price = i, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, 30000)]
        
        time_deltas_allocated = time.time()

        snapshot1 = OrderBookSnapshot()
        snapshot1.apply(deltas)

        time_snapshot_applied = time.time()

        # print(f"30000 unique deltas allocated: {time_deltas_allocated - time_start}")
        # print(f"30000 unique deltas applied: {time_snapshot_applied - time_deltas_allocated}")

    def test_apply_seems_quick_few_unique_keys(self):
        time_start = time.time()

        deltas = [OrderBookDelta(timestamp = (float)(i), price = i % 100, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, 30000)]
        
        time_deltas_allocated = time.time()

        snapshot1 = OrderBookSnapshot()
        snapshot1.apply(deltas)

        time_snapshot_applied = time.time()

        # print(f"30000 dup deltas allocated: {time_deltas_allocated - time_start}")
        # print(f"30000 dup deltas applied: {time_snapshot_applied - time_deltas_allocated}")

    # def test_binning_performance(self):
    #     return
    #     factors = [1, 2, 3]
    #     modes = [1]
    #     sizes = [100, 150, 250]
    #     for factor in factors:
    #         for mode in modes:
    #             for how_many in sizes:
    #                 snapshot1 = OrderBookSnapshot()
    #                 deltas = [OrderBookDelta(timestamp = datetime.datetime.now(), price = i, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, how_many)]
    #                 for index in range(1, 10):
    #                     new_deltas = [OrderBookDelta(timestamp = datetime.datetime.now(), price = i % 10, quantity = i / 2 if (i % 2 == 0) else i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, (int)(how_many / 2)]
    #                     bins = range(1, (int)( how_many / factor), 5)
    #                     snapshot1.apply(deltas)
    #                     time_applied = datetime.datetime.now()
    #                     bins_output = snapshot1.calculate_bid_ask_differential_bins(bins, mode)
    #                     time_binned = datetime.datetime.now()
    #                     print(f"Mode {mode} - It took {(time_binned - time_applied).microseconds} μs to bin {len(deltas)} objects in to {len(bins) - 1} bins with 1/{factor} of them relevant")

                    #print(bins_output)

    def test_bin(self):
        n=100
        x = np.zeros((n,100))
        factors = [1, 2, 3]
        modes = [1]
        sizes = [100, 150, 200, 250, 300, 350]
        should_saves = [True, False]
        for should_save in should_saves:
            for mode in modes:
                for how_many in sizes:
                    print(f"should_save = {should_save} and mode = {mode} and how_many = {how_many}")
                    for j in range(5):
                        snapshot1 = OrderBookSnapshot(save_messages = should_save)
                        deltas = [OrderBookDelta(timestamp = (float)(i), price = i%101, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, how_many*n+1)]
                        init_deltas = [OrderBookDelta(timestamp = (float)(i), price = i%97, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, how_many*n+1)]
                        snapshot1.apply(init_deltas)
                        time_initialized = datetime.datetime.now()
                        for i in range(n):
                            bins = list(range(101))
                            snapshot1.apply(deltas[i*how_many:(i+1)*how_many])
                            bins_output = snapshot1.calculate_bid_ask_differential_bins(bins, mode)
                            x[i] = bins_output
                        time_binned = datetime.datetime.now()
                        print(f"Mode {mode} - It took {(time_binned - time_initialized).microseconds} μs to bin {len(deltas)} objects in to {len(bins) - 1} bins over {n} snapshots")

    def test_bin_raw(self):
        n=100
        x = np.zeros((n,100))
        factors = [1, 2, 3]
        modes = [1]
        sizes = [100, 150, 200, 250, 300, 350]
        for mode in modes:
            for how_many in sizes:
                snapshot1 = OrderBookSnapshot()
                
                deltas = []

                how_many_delta = how_many * n + 1

                for delta_i in range(1, how_many_delta):
                    deltas.append((float)(delta_i))
                    deltas.append(delta_i % 101)
                    deltas.append(delta_i if (delta_i % 2 == 0) else -delta_i)
                    
                init_deltas = []

                for delta_i in range(1, how_many_delta):
                    init_deltas.append((float)(delta_i))
                    init_deltas.append(delta_i % 97)
                    init_deltas.append(delta_i if (delta_i % 2 == 0) else -delta_i)

                #deltas = [OrderBookDelta(timestamp = (float)(i), price = i%101, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, how_many*n+1)]
                #init_deltas = [OrderBookDelta(timestamp = (float)(i), price = i%97, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, how_many*n+1)]
                snapshot1.apply(init_deltas)
                time_initialized = datetime.datetime.now()
                for i in range(n):
                    bins = list(range(101))
                    snapshot1.apply(deltas[i*how_many*3:(i+1)*how_many*3])
                    bins_output = snapshot1.calculate_bid_ask_differential_bins(bins, mode)
                    x[i] = bins_output
                time_binned = datetime.datetime.now()
                print(f"Mode {mode} - It took {(time_binned - time_initialized).microseconds} μs to bin {len(deltas)/3} objects in to {len(bins) - 1} bins over {n} snapshots")

if __name__ == '__main__':
    unittest.main()