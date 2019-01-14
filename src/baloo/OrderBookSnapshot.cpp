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

void OrderBookSnapshot::apply(ImmutableOrderBookSnapshot& snapshot) {
    apply(snapshot.getAsks(), snapshot.getBids());
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
    if (concatenatedDeltas.size() % 3 != 0) {
        throw "Deltas must be defined in tuples of three (timestamp, price, quantity)";
    }
    
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
    delete this->initialSnapshot;
    this->initialSnapshot = new ImmutableOrderBookSnapshot(asks, bids);
    this->asks = asks;
    this->bids = bids;
    this->deltas.clear();
}

std::vector<std::vector<double>> OrderBookSnapshot::applyAndBucket(std::vector<OrderBookUpdate>& updates, std::vector<double>& timeBuckets, std::vector<double>& bins, bool ignoreDeltasBeforeBeginningOfFirstBin, bool calculateBidAskSpreadFeatures) {
    if (updates.size() < 1) {
        throw "At least one delta must be provided.";
    }
    if (timeBuckets.size() < 2) {
        throw "At least one time bucket must be defined. (N points defines N - 1 time buckets.)";
    }
    if (bins.size() < 2) {
        throw "At least one bin must be defined. (N points defines N - 1 bins.)";
    }
    
    std::vector<std::vector<double>> bucketsList(timeBuckets.size() - 1);
    
    std::vector<OrderBookUpdate>::iterator updateIterator = updates.begin();
    
    while (updateIterator != updates.end()) {
        double timestamp;

        OrderBookUpdate& update = *updateIterator;
        if (std::holds_alternative<OrderBookDelta>(update)) {
            auto unwrappedDelta = std::get<OrderBookDelta>(update);
            timestamp = unwrappedDelta.getTimestamp();
        }
        else if (std::holds_alternative<ImmutableOrderBookSnapshot>(update)) {
            auto unwrappedSnapshot = std::get<ImmutableOrderBookSnapshot>(update);
            timestamp = unwrappedSnapshot.getTimestamp();
        }
        if (timestamp >= timeBuckets[0]) {
            break;
        } else {
            if (!ignoreDeltasBeforeBeginningOfFirstBin) {
                if (std::holds_alternative<OrderBookDelta>(update)) {
                    auto unwrappedDelta = std::get<OrderBookDelta>(update);
                    apply(unwrappedDelta);
                }
                else if (std::holds_alternative<ImmutableOrderBookSnapshot>(update)) {
                    auto unwrappedSnapshot = std::get<ImmutableOrderBookSnapshot>(update);
                    apply(unwrappedSnapshot);
                }
            }
            ++updateIterator;
        }
    }

    if (updateIterator == updates.end()) return bucketsList;

    for (std::vector<double>::iterator leftBucketIterator = timeBuckets.begin(); leftBucketIterator != timeBuckets.end() - 1; ++leftBucketIterator) {
        double leftBucketValue = *leftBucketIterator;
        double rightBucketValue = *(leftBucketIterator + 1);
        OrderBookUpdate& update = *updateIterator;
        double timestamp;
        if (std::holds_alternative<OrderBookDelta>(update)) {
            auto unwrappedDelta = std::get<OrderBookDelta>(update);
            timestamp = unwrappedDelta.getTimestamp();
        }
        else if (std::holds_alternative<ImmutableOrderBookSnapshot>(update)) {
            auto unwrappedSnapshot = std::get<ImmutableOrderBookSnapshot>(update);
            timestamp = unwrappedSnapshot.getTimestamp();
        }
        while (timestamp >= leftBucketValue && timestamp < rightBucketValue && updateIterator != updates.end()) {
            if (std::holds_alternative<OrderBookDelta>(update)) {
                auto unwrappedDelta = std::get<OrderBookDelta>(update);
                apply(unwrappedDelta);
            }
            else if (std::holds_alternative<ImmutableOrderBookSnapshot>(update)) {
                auto unwrappedSnapshot = std::get<ImmutableOrderBookSnapshot>(update);
                apply(unwrappedSnapshot);
            }
            ++updateIterator;

            if (updateIterator != updates.end()) {
                update = *updateIterator;
                if (std::holds_alternative<OrderBookDelta>(update)) {
                    auto unwrappedDelta = std::get<OrderBookDelta>(update);
                    timestamp = unwrappedDelta.getTimestamp();
                }
                else if (std::holds_alternative<ImmutableOrderBookSnapshot>(update)) {
                    auto unwrappedSnapshot = std::get<ImmutableOrderBookSnapshot>(update);
                    timestamp = unwrappedSnapshot.getTimestamp();
                }
            }
        }
        auto bucketsListItem = calculateBidAskDifferentialBins(bins);

        if (calculateBidAskSpreadFeatures) {
            double bestAskPrice, bestAskQuantity, bestBidPrice, bestBidQuantity, bidAskSpread, midPrice;
            if (asks.empty()) {
                bestAskPrice = 0;
                bestAskQuantity = 0;
            } else {
                auto bestAsk = asks.begin();
                bestAskPrice = bestAsk->first;
                bestAskQuantity = bestAsk->second;
            }
            if (bids.empty()) {
                bestBidPrice = 0;
                bestBidQuantity = 0;
            } else {
                auto bestBid = --(bids.end());
                bestBidPrice = bestBid->first;
                bestBidQuantity = bestBid->second;
            }
            if (asks.empty() || bids.empty()) {
                bidAskSpread = 0;
            } else {
                bidAskSpread = bestAskPrice - bestBidPrice;
            }
            
            //bucketsListItem.insert(bucketsListItem.end(), { bidAskSpread, bestAskQuantity, bestBidQuantity });
            bucketsListItem->insert(bucketsListItem->end(), { bestBidPrice, bestAskPrice, bestBidQuantity, bestAskQuantity });
        }

        bucketsList[leftBucketIterator - timeBuckets.begin()] = *bucketsListItem;

    }
    
    return bucketsList;
}

OrderBookSnapshot* OrderBookSnapshot::getSnapshotAtPointInTime(double pointInTime) {
    if (!saveMessages) {
        throw "Cannot get snapshot at point in time when saveMessages is false.";
    }

    OrderBookSnapshot* snapshot = new OrderBookSnapshot(initialSnapshot);
    std::map<double,OrderBookDelta>::iterator upperIterator = deltas.upper_bound(pointInTime);

    for(std::map<double,OrderBookDelta>::iterator it = deltas.begin(); it != deltas.upper_bound(pointInTime); ++it) {
        snapshot->apply(it->second);
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