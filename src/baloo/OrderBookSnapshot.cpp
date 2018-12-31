#include "OrderBookSnapshot.h"

#include <map>
#include <vector>
#include <algorithm>
#include <ctime>
#include <cmath>

#include "OrderBookDelta.h"

void OrderBookSnapshot::apply(OrderBookDelta& delta) {
    if (saveMessages)
        deltas.emplace(delta.getTimestamp(), delta);
    auto & whichMap = (delta.getDirection() == OrderDirection::Ask) ? asks : bids;
    if (delta.getQuantity() > 0)
        whichMap[delta.getPrice()] = delta.getQuantity();
    else
        whichMap.erase(delta.getPrice());
}

void OrderBookSnapshot::apply(std::vector<OrderBookDelta> &deltas) {
    for (OrderBookDelta& delta: deltas) {
        apply(delta);
    }
}

void OrderBookSnapshot::apply(double timestamp, double price, double quantity, OrderDirection::OrderDirectionEnum direction) {
    if (saveMessages)
        deltas.emplace(timestamp, *new OrderBookDelta(timestamp, price, quantity, direction));
    auto & whichMap = (direction == OrderDirection::Ask) ? asks : bids;
    if (quantity > 0)
        whichMap[price] = quantity;
    else
        whichMap.erase(price);
}

void OrderBookSnapshot::apply(std::vector<std::tuple<double, double, double, OrderDirection::OrderDirectionEnum>>& deltas) {
    for (std::tuple<double, double, double, OrderDirection::OrderDirectionEnum>& delta : deltas) {
        apply(std::get<0>(delta), std::get<1>(delta), std::get<2>(delta), std::get<3>(delta));
    }
}

void OrderBookSnapshot::apply(std::vector<double>& concatenatedDeltas) {
    int numberOfDeltas = concatenatedDeltas.size() / 3;
    for (int i = 0; i < numberOfDeltas; i++) {
        double timestamp = concatenatedDeltas[3 * i + 0];
        double price = concatenatedDeltas[3 * i + 1];
        double quantityRaw = concatenatedDeltas[3 * i + 2];
        OrderDirection::OrderDirectionEnum direction = (quantityRaw >= 0) ? OrderDirection::Bid : OrderDirection::Ask;
        double quantity = std::abs(quantityRaw);
        apply(timestamp, price, quantity, direction);
    }
}

void OrderBookSnapshot::apply(std::map<double, double>& asks, std::map<double, double>& bids) {
    this->initialSnapshot = *new ImmutableOrderBookSnapshot(asks, bids);
    this->asks = asks;
    this->bids = bids;
    this->deltas.clear();
}

OrderBookSnapshot& OrderBookSnapshot::getSnapshotAtPointInTime(double pointInTime) {
    if (!saveMessages) {
        throw "Cannot get snapshot at point in time when saveMessages is false.";
    }

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