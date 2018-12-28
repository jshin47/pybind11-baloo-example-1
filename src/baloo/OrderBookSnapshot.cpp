#include "OrderBookSnapshot.h"

#include <map>
#include <vector>
#include <algorithm>
#include <ctime>

#include "OrderBookDelta.h"

void OrderBookSnapshot::apply(OrderBookDelta &delta) {
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

OrderBookSnapshot& OrderBookSnapshot::getSnapshotAtPointInTime(TimeType& pointInTime) {
    OrderBookSnapshot& snapshot = *new OrderBookSnapshot();
    std::map<TimeType,OrderBookDelta>::iterator upperIterator = deltas.upper_bound(pointInTime);

    for(std::map<TimeType,OrderBookDelta>::iterator it = deltas.begin(); it != deltas.upper_bound(pointInTime); ++it) {
        snapshot.apply(it->second);
    }

    return snapshot;
}

void applyBinsValues(std::vector<double> &bins, std::vector<double> &binsValues, std::map<double, double> &priceMap, OrderDirection::OrderDirectionEnum direction) {
    int multiplier = (direction == OrderDirection::Ask) ? -1 : 1;
    for (auto elem : priceMap) {
        bool biggerThanOrEqualToSmallestBinElement = elem.first >= bins[0];
        bool smallerThanBiggestBinElement = elem.first < bins[bins.size() - 1];
        if (biggerThanOrEqualToSmallestBinElement && smallerThanBiggestBinElement) {
            auto whichBin = std::upper_bound(bins.begin(), bins.end(), elem.first);
            int position = whichBin - bins.begin() - 1;
            binsValues[position] = binsValues[position] + multiplier * elem.second;
        } else if (!smallerThanBiggestBinElement)
            break;
    }
}

std::vector<double>& OrderBookSnapshot::calculateBidAskSpreads(std::vector<double> &bins) {
    std::vector<double>& binsValues = *new std::vector<double>(bins.size() - 1, 0);

    applyBinsValues(bins, binsValues, asks, OrderDirection::Ask);
    applyBinsValues(bins, binsValues, bids, OrderDirection::Bid);
    
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