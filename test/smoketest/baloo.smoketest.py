import unittest

import datetime
import time

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

class BalooModuleTests(unittest.TestCase):

    def setUp(self):
        self._started_at = time.time()
    
    def tearDown(self):
        elapsed = time.time() - self._started_at

    def test_orderbook_delta_retains_values(self):
        delta1 = OrderBookDelta()
        timestamp = datetime.datetime.now()
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
        delta1.timestamp = datetime.datetime.now()
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        snapshot1.apply(delta1)
        delta2 = OrderBookDelta()
        delta2.timestamp = datetime.datetime.now()
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply(delta2)
        self.assertEqual(len(snapshot1.asks), 1)
        self.assertEqual(len(snapshot1.bids), 1)

    def test_orderbook_snapshot_applies_list(self):
        snapshot1 = OrderBookSnapshot()
        delta1 = OrderBookDelta()
        delta1.timestamp = datetime.datetime.now()
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        delta2 = OrderBookDelta()
        delta2.timestamp = datetime.datetime.now()
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply([delta1, delta2])
        self.assertEqual(len(snapshot1.asks), 1)
        self.assertEqual(len(snapshot1.bids), 1)

    def test_get_snapshot_at_point_in_time(self):
        snapshot1 = OrderBookSnapshot()
        delta1 = OrderBookDelta()
        delta1.timestamp = datetime.datetime.now()
        delta1.quantity = 1
        delta1.direction = OrderDirection.Ask
        delta2 = OrderBookDelta()
        delta2.timestamp = datetime.datetime.now()
        delta2.quantity = 1
        delta2.direction = OrderDirection.Bid
        snapshot1.apply([delta1, delta2])
        snapshot2 = snapshot1.get_snapshot_at_point_in_time(delta1.timestamp)
        self.assertEqual(len(snapshot2.asks), 1)
        self.assertEqual(len(snapshot2.bids), 0)

    def test_apply_seems_quick_many_unique_keys(self):
        time_start = time.time()

        deltas = [OrderBookDelta(timestamp = datetime.datetime.now(), price = i, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, 30000)]
        
        time_deltas_allocated = time.time()

        snapshot1 = OrderBookSnapshot()
        snapshot1.apply(deltas)

        time_snapshot_applied = time.time()

        print(f"30000 unique deltas allocated: {time_deltas_allocated - time_start}")
        print(f"30000 unique deltas applied: {time_snapshot_applied - time_deltas_allocated}")

    def test_apply_seems_quick_few_unique_keys(self):
        time_start = time.time()

        deltas = [OrderBookDelta(timestamp = datetime.datetime.now(), price = i % 100, quantity = i, direction = OrderDirection.Ask if (i % 2 == 0) else OrderDirection.Bid ) for i in range(1, 30000)]
        
        time_deltas_allocated = time.time()

        snapshot1 = OrderBookSnapshot()
        snapshot1.apply(deltas)

        time_snapshot_applied = time.time()

        print(f"30000 dup deltas allocated: {time_deltas_allocated - time_start}")
        print(f"30000 dup deltas applied: {time_snapshot_applied - time_deltas_allocated}")

if __name__ == '__main__':
    unittest.main()