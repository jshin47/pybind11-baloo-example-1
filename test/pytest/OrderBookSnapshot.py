import datetime
import time
from operator import eq

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot

from PythonBasedOrderBookSnapshot import PythonBasedOrderBookSnapshot

def pytest_generate_tests(metafunc):
    if 'save_messages' in metafunc.fixturenames:
        metafunc.parametrize("save_messages", [True, False])
    if 'count_of_each_side' in metafunc.fixturenames:
        metafunc.parametrize("count_of_each_side", [100, 1000])

def assert_snapshots_asks_and_bids_are_equal(A, B):
    assert eq(A.asks, B.asks) == True
    assert eq(A.bids, B.bids) == True

def test_orderbook_snapshot_apply_saves_and_zeroes_appropriately(save_messages, count_of_each_side):
    snapshot_cpp = OrderBookSnapshot(saveMessages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = save_messages)

    def apply_to_both_snapshots(delta):
        snapshot_cpp.apply(delta)
        snapshot_py.apply(delta)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    for i in range(1, count_of_each_side + 1):
        if (i % 3 == 0):
            apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, 0, OrderDirection.Ask))
            apply_to_both_snapshots(OrderBookDelta(time.time(), i, 0, OrderDirection.Bid))
    
    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    for i in range(3, count_of_each_side + 1, 3):
        assert snapshot_cpp.asks.get(i, None) == None
        assert snapshot_cpp.bids.get(i, None) == None

def test_orderbook_snapshot_repeated_apply_is_idempotent(save_messages, count_of_each_side):
    snapshot_cpp = OrderBookSnapshot(saveMessages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = save_messages)

    def apply_to_both_snapshots(delta):
        snapshot_cpp.apply(delta)
        snapshot_py.apply(delta)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    for _ in range(10):
        for i in range(1, count_of_each_side + 1):
            snapshot_cpp.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
            snapshot_cpp.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))
    
    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

def test_apply_overwrites_appropriately(save_messages):
    count_of_each_side = 100

    snapshot_cpp = OrderBookSnapshot(saveMessages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = save_messages)

    def apply_to_both_snapshots(delta):
        snapshot_cpp.apply(delta)
        snapshot_py.apply(delta)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    asks_before = dict(snapshot_cpp.asks)
    bids_before = dict(snapshot_cpp.bids)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i + 17.3, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i + 17.3, OrderDirection.Bid))

    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    for i in range(1, count_of_each_side + 1):
        assert snapshot_cpp.asks[i + count_of_each_side] == asks_before[i + count_of_each_side] + 17.3
        assert snapshot_cpp.bids[i] == bids_before[i] + 17.3

def test_cpp_apply_is_faster_than_py_apply(save_messages, count_of_each_side):

    snapshot_cpp = OrderBookSnapshot(saveMessages = False)

    time_cpp_start = datetime.datetime.now()

    for i in range(1, count_of_each_side + 1):
        snapshot_cpp.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        snapshot_cpp.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    time_cpp_end = datetime.datetime.now()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = False)

    time_py_start = datetime.datetime.now()

    for i in range(1, count_of_each_side + 1):
        snapshot_py.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        snapshot_py.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    time_py_end = datetime.datetime.now()
    time_py = time_py_end - time_cpp_start

    time_py_to_cpp_ratio = time_py / time_cpp

    assert time_py_to_cpp_ratio > 1
    



