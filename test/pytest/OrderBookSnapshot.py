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
    if 'bin_factor' in metafunc.fixturenames:
        metafunc.parametrize("bin_factor", [0, 0.1, 0.2, 0.25, 1/3, 0.4])
    if 'bin_step' in metafunc.fixturenames:
        metafunc.parametrize("bin_step", [1, 2, 5, 10, 20])

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

def test_cpp_apply_is_faster_than_py_apply_individual(save_messages):
    count_of_each_side = 100000

    snapshot_cpp = OrderBookSnapshot(saveMessages = False)

    time_cpp_start = time.time()

    for i in range(1, count_of_each_side + 1):
        snapshot_cpp.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        snapshot_cpp.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = False)

    time_py_start = time.time()

    for i in range(1, count_of_each_side + 1):
        snapshot_py.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        snapshot_py.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    time_py_end = time.time()
    time_py = time_py_end - time_py_start

    time_py_to_cpp_ratio = time_py / time_cpp

    assert time_py_to_cpp_ratio > 1.5

def test_cpp_apply_is_much_faster_than_py_apply_list(save_messages):
    count_of_each_side = 100000

    snapshot_cpp = OrderBookSnapshot(saveMessages = False)

    asks_to_apply = [OrderBookDelta(timestamp = time.time(), price = i + count_of_each_side, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    bids_to_apply = [OrderBookDelta(timestamp = time.time(), price = i, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]

    time_cpp_start = time.time()

    snapshot_cpp.apply(asks_to_apply)
    snapshot_cpp.apply(bids_to_apply)

    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = False)

    time_py_start = time.time()

    for ask_to_apply in asks_to_apply:
        snapshot_py.apply(ask_to_apply)
    for bid_to_apply in bids_to_apply:
        snapshot_py.apply(bid_to_apply)
    
    time_py_end = time.time()
    time_py = time_py_end - time_py_start

    time_py_to_cpp_ratio = time_py / time_cpp

    assert time_py_to_cpp_ratio > 10

def test_binning_works(save_messages, count_of_each_side, bin_factor, bin_step):
    snapshot_cpp = OrderBookSnapshot(saveMessages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(saveMessages = save_messages)

    def apply_to_both_snapshots(delta):
        snapshot_cpp.apply(delta)
        snapshot_py.apply(delta)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    bin_left = ((int)(bin_factor * (count_of_each_side * 2 + 1)))
    bin_right = ((int)((1 - bin_factor) * (count_of_each_side * 2 + 1)))

    bins = list(range(bin_left, bin_right, bin_step))

    bins_output_cpp = snapshot_cpp.calculate_bid_ask_differential_bins(bins)
    bins_output_py = snapshot_py.calculate_bid_ask_differential_bins(bins)
    #print(bins_output_cpp)
    #print(bins_output_py)
    assert len(bins_output_cpp) == len(bins) - 1
    assert len(bins_output_cpp) == len(bins_output_py)
    assert eq(bins_output_cpp, bins_output_py) == True
    