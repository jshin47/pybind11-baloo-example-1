#include "OrderBookSnapshot.h"

#include <map>
#include <vector>
#include <algorithm>
#include <ctime>

#include "OrderBookDelta.h"

void OrderBookSnapshot::apply(OrderBookDelta& delta) {
    deltas.emplace(delta.getTimestamp(), delta);
    auto & whichMap = (delta.getDirection() == OrderDirection::Ask) ? asks : bids;
    if (delta.getQuantity() > 0)
        whichMap.emplace(delta.getPrice(), delta.getQuantity());
    else
        whichMap.erase(delta.getPrice());
}

void OrderBookSnapshot::apply(std::vector<OrderBookDelta> &deltas) {
    for (OrderBookDelta& delta: deltas) {
        apply(delta);
    }
}

void OrderBookSnapshot::become(std::map<double, double>& asks, std::map<double, double>& bids) {
    this->initialSnapshot = *new ImmutableOrderBookSnapshot(asks, bids);
    this->asks = asks;
    this->bids = bids;
    this->deltas.clear();
}

OrderBookSnapshot& OrderBookSnapshot::getSnapshotAtPointInTime(double pointInTime) {
    OrderBookSnapshot& snapshot = *new OrderBookSnapshot(initialSnapshot);
    std::map<double,OrderBookDelta>::iterator upperIterator = deltas.upper_bound(pointInTime);

    for(std::map<double,OrderBookDelta>::iterator it = deltas.begin(); it != deltas.upper_bound(pointInTime); ++it) {
        snapshot.apply(it->second);
    }

    return snapshot;
}

std::map<double, OrderBookDelta>& OrderBookSnapshot::getDeltas() {
    return deltas;
}

std::map<double, double>& OrderBookSnapshot::getAsks() {
    return asks;
}

std::map<double, double>& OrderBookSnapshot::getBids() {
    return bids;
}