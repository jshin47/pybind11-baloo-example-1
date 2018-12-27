#include "OrderBookSnapshot.h"

#include <map>
#include <vector>
#include <algorithm>
#include <ctime>

#include "OrderBookDelta.h"

void OrderBookSnapshot::apply(OrderBookDelta &delta) {
    deltas.emplace(delta.getTimestamp(), delta);
    auto & whichMap = (delta.getDirection() == Ask) ? asks : bids;
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

OrderBookSnapshot& OrderBookSnapshot::getSnapshotAtPointInTime(TimeType& pointInTime) {
    OrderBookSnapshot& snapshot = *new OrderBookSnapshot();
    std::map<TimeType,OrderBookDelta>::iterator upperIterator = deltas.upper_bound(pointInTime);

    for(std::map<TimeType,OrderBookDelta>::iterator it = deltas.begin(); it != deltas.upper_bound(pointInTime); ++it) {
        snapshot.apply(it->second);
    }

    return snapshot;
}

std::vector<double>& OrderBookSnapshot::calculateBidAskSpreads(std::vector<double> &bins) {
    std::vector<double>& binsValues = *new std::vector<double>(bins.size(), 0);
    
    for (auto elem : asks) {
        if (elem.first >= binsValues[0] && elem.first <= binsValues[binsValues.size() - 1]) {
            auto whichBin = std::upper_bound(bins.begin(), bins.end(), elem.first);
            int position = whichBin - bins.begin() - 1;
            binsValues[position] = binsValues[position] - elem.second;
        }
    }

    for (auto elem : bids) { 
        if (elem.first >= binsValues[0] && elem.first <= binsValues[binsValues.size() - 1]) {
            auto whichBin = std::upper_bound(bins.begin(), bins.end(), elem.first);
            int position = whichBin - bins.begin() + 1;
            binsValues[position] = binsValues[position] - elem.second;
        }
    }
    
    return binsValues;
}

std::map<TimeType, OrderBookDelta> OrderBookSnapshot::getDeltas() {
    return deltas;
}

std::map<double, double> OrderBookSnapshot::getAsks() {
    return asks;
}

std::map<double, double> OrderBookSnapshot::getBids() {
    return bids;
}