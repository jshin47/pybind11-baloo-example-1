import unittest

import datetime
import timeit

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

class BalooModuleTests(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()