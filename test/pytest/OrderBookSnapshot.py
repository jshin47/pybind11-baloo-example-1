import datetime
import time
from operator import eq

from baloo import OrderDirection, OrderBookDelta, OrderBookSnapshot, ImmutableOrderBookSnapshot

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
    if 'time_buckets_count' in metafunc.fixturenames:
        metafunc.parametrize("time_buckets_count", [2, 5, 10, 20, 50])

def assert_snapshots_asks_and_bids_are_equal(A, B):
    assert eq(A.asks, B.asks) == True
    assert eq(A.bids, B.bids) == True

def test_orderbook_snapshot_apply_saves_and_zeroes_appropriately(save_messages, count_of_each_side):
    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)

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
    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)

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

    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)

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

def test_cpp_apply_is_faster_than_austins_super_slow_python_implementation(save_messages):

    count_of_each_side = 100000

    snapshot_cpp = OrderBookSnapshot(save_messages = False)
    deltas = [OrderBookDelta(1, i + count_of_each_side, i, OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    deltas = deltas + [OrderBookDelta(1, i, i, OrderDirection.Bid) for i in range(1, count_of_each_side + 1)]
    
    time_cpp_start = time.time()

    for delta in deltas:
        snapshot_cpp.apply(delta)

    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = False)

    time_py_start = time.time()

    for i in range(1, count_of_each_side + 1):
        snapshot_py.apply_fast(['sell', i + count_of_each_side, i])
        snapshot_py.apply_fast(['buy', i, i])

    time_py_end = time.time()
    time_py = time_py_end - time_py_start

    time_py_to_cpp_ratio = time_py / time_cpp
    print(time_py_to_cpp_ratio)
    assert time_py_to_cpp_ratio > 1.0

def test_cpp_apply_is_faster_than_py_apply_individual(save_messages):
    count_of_each_side = 100000

    snapshot_cpp = OrderBookSnapshot(save_messages = False)

    time_cpp_start = time.time()

    for i in range(1, count_of_each_side + 1):
        snapshot_cpp.apply(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        snapshot_cpp.apply(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = False)

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

    snapshot_cpp = OrderBookSnapshot(save_messages = False)

    asks_to_apply = [OrderBookDelta(timestamp = time.time(), price = i + count_of_each_side, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    bids_to_apply = [OrderBookDelta(timestamp = time.time(), price = i, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]

    time_cpp_start = time.time()

    snapshot_cpp.apply(asks_to_apply)
    snapshot_cpp.apply(bids_to_apply)

    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = False)

    time_py_start = time.time()

    for ask_to_apply in asks_to_apply:
        snapshot_py.apply(ask_to_apply)
    for bid_to_apply in bids_to_apply:
        snapshot_py.apply(bid_to_apply)
    
    time_py_end = time.time()
    time_py = time_py_end - time_py_start

    time_py_to_cpp_ratio = time_py / time_cpp

    assert time_py_to_cpp_ratio > 5

def test_binning_works(save_messages, count_of_each_side, bin_factor, bin_step):
    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)

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

    assert len(bins_output_cpp) == len(bins) - 1
    assert len(bins_output_cpp) == len(bins_output_py)
    assert eq(bins_output_cpp, bins_output_py) == True
    
def test_binning_is_much_faster(save_messages):
    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)

    count_of_each_side = 10000

    def apply_to_both_snapshots(delta):
        snapshot_cpp.apply(delta)
        snapshot_py.apply(delta)

    for i in range(1, count_of_each_side + 1):
        apply_to_both_snapshots(OrderBookDelta(time.time(), i + count_of_each_side, i, OrderDirection.Ask))
        apply_to_both_snapshots(OrderBookDelta(time.time(), i, i, OrderDirection.Bid))

    assert_snapshots_asks_and_bids_are_equal(snapshot_cpp, snapshot_py)

    bin_left = 1500
    bin_right = 9000
    bin_step = 15

    bins = list(range(bin_left, bin_right, bin_step))

    time_cpp_start = time.time()
    bins_output_cpp = snapshot_cpp.calculate_bid_ask_differential_bins(bins)
    time_cpp_end = time.time()
    time_cpp = time_cpp_end - time_cpp_start

    time_py_start = time.time()
    bins_output_py = snapshot_py.calculate_bid_ask_differential_bins(bins)
    time_py_end = time.time()
    time_py = time_py_end - time_py_start
    
    time_py_to_cpp_ratio = time_py / time_cpp

    assert time_py_to_cpp_ratio > 100

# TODO: Implement this in PythonBasedOrderBookSnapshot a different way and compare.
def test_apply_with_time_buckets_output_looks_correct(save_messages, time_buckets_count, bin_factor, bin_step):
    count_of_each_side = 100
    bin_left = ((int)(bin_factor * (count_of_each_side * 2 + 1)))
    bin_right = ((int)((1 - bin_factor) * (count_of_each_side * 2 + 1)))

    bins = list(range(bin_left, bin_right, bin_step))

    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)
    bids_to_apply = [OrderBookDelta(timestamp = i, price = i, quantity = i, direction = OrderDirection.Bid) for i in range(1, count_of_each_side + 1)]
    asks_to_apply = [OrderBookDelta(timestamp = count_of_each_side + i, price = i + count_of_each_side, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    to_apply = bids_to_apply + asks_to_apply

    time_bucket_step = ((int)(2 * count_of_each_side / time_buckets_count))
    time_buckets = range(2, 2*count_of_each_side+1, time_bucket_step)

    timebucket_bins_cpp = snapshot_cpp.apply_and_bucket(to_apply, time_buckets, bins)
    timebucket_bins_py = snapshot_py.apply_and_bucket(to_apply, time_buckets, bins)
    assert eq(timebucket_bins_cpp, timebucket_bins_py) == True

def test_apply_with_time_buckets_cpp_is_much_faster(save_messages):
    count_of_each_side = 2500
    time_buckets_count = 50
    bin_factor = 0.2
    bin_left = ((int)(bin_factor * (count_of_each_side * 2 + 1)))
    bin_right = ((int)((1 - bin_factor) * (count_of_each_side * 2 + 1)))
    bin_step = 20

    bins = list(range(bin_left, bin_right, bin_step))

    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)
    bids_to_apply = [OrderBookDelta(timestamp = i, price = i, quantity = i, direction = OrderDirection.Bid) for i in range(1, count_of_each_side + 1)]
    asks_to_apply = [OrderBookDelta(timestamp = count_of_each_side + i, price = i + count_of_each_side, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    to_apply = bids_to_apply + asks_to_apply

    time_bucket_step = ((int)(2 * count_of_each_side / time_buckets_count))
    time_buckets = range(2, 2*count_of_each_side+1, time_bucket_step)

    time_applied_bucketed_cpp_start = time.time()
    timebucket_bins_cpp = snapshot_cpp.apply_and_bucket(to_apply, time_buckets, bins)
    time_applied_bucketed_cpp_end = time.time()
    time_applied_bucketed_cpp = time_applied_bucketed_cpp_end - time_applied_bucketed_cpp_start
    
    time_applied_bucketed_py_start = time.time()
    timebucket_bins_py = snapshot_py.apply_and_bucket(to_apply, time_buckets, bins)
    time_applied_bucketed_py_end = time.time()
    time_applied_bucketed_py = time_applied_bucketed_py_end - time_applied_bucketed_py_start
    
    assert eq(timebucket_bins_cpp, timebucket_bins_py) == True
    
    time_applied_bucketed_py_to_cpp_ratio = time_applied_bucketed_py / time_applied_bucketed_cpp

    assert time_applied_bucketed_py_to_cpp_ratio > 100

    assert time_applied_bucketed_cpp < count_of_each_side * 0.00001

def test_can_apply_with_snapshots_and_deltas(save_messages):
    count_of_each_side = 100
    time_buckets_count = 20
    bin_factor = 0.15
    bin_step = 10
    bin_left = ((int)(bin_factor * (count_of_each_side * 2 + 1)))
    bin_right = ((int)((1 - bin_factor) * (count_of_each_side * 2 + 1)))

    bins = list(range(bin_left, bin_right, bin_step))

    snapshot_cpp = OrderBookSnapshot(save_messages = save_messages)
    snapshot_py = PythonBasedOrderBookSnapshot(save_messages = save_messages)
    bids_to_apply = [OrderBookDelta(timestamp = i, price = i, quantity = i, direction = OrderDirection.Bid) for i in range(1, count_of_each_side + 1)]
    asks_to_apply = [OrderBookDelta(timestamp = count_of_each_side + i, price = i + count_of_each_side, quantity = i, direction = OrderDirection.Ask) for i in range(1, count_of_each_side + 1)]
    deltas_to_apply = bids_to_apply + asks_to_apply
    
    snapshot_asks = {
        110: 6.66
    }
    snapshot_bids = {
        111: 7.77
    }
    snapshot = ImmutableOrderBookSnapshot(asks = snapshot_asks, bids = snapshot_bids, timestamp = count_of_each_side * 2 + 1)

    updates_to_apply = deltas_to_apply + [snapshot]

    time_bucket_step = ((int)(2 * count_of_each_side / time_buckets_count))
    time_buckets = list(range(2, 2*count_of_each_side+time_bucket_step, time_bucket_step))
    print(time_buckets)
    print(count_of_each_side * 2)

    timebucket_bins_cpp = snapshot_cpp.apply_and_bucket(updates_to_apply, time_buckets, bins)
    print(timebucket_bins_cpp)
    