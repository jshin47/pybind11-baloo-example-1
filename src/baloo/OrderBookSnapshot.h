#ifndef __BALOO_ORDERBOOK_SNAPSHOT_H__
#define __BALOO_ORDERBOOK_SNAPSHOT_H__

#include <vector>
#include <map>
#include <chrono>
#include <string>
#include <memory>
#include <tuple>

#include "definitions.h"
#include "AbsOrderBookSnapshot.h"
#include "ImmutableOrderBookSnapshot.h"
#include "OrderBookDelta.h"

class OrderBookSnapshot : public AbsOrderBookSnapshot {
public:
    void apply(OrderBookDelta& delta);
    void apply(std::vector<OrderBookDelta>& deltas);
    void apply(double timestamp, double price, double quantity, OrderDirection::OrderDirectionEnum direction);
    void apply(std::vector<std::tuple<double, double, double, OrderDirection::OrderDirectionEnum>>& deltas);
    void apply(std::vector<double>& concatenatedDeltas);
    void apply(std::map<double, double>& asks, std::map<double, double>& bids);
    std::vector<std::vector<double>>& applyAndBucket(std::vector<OrderBookDelta>& deltas, std::vector<double>& timeBuckets, std::vector<double>& bins, bool ignoreDeltasBeforeBeginningOfFirstBin = true);
    OrderBookSnapshot& getSnapshotAtPointInTime(double pointInTime);

    std::map<double, OrderBookDelta>& getDeltas();
    std::map<double, double>& getAsks();
    std::map<double, double>& getBids();

    OrderBookSnapshot(bool saveMessages = true) {
        this->saveMessages = saveMessages;
    }

    OrderBookSnapshot(std::map<double, double>& asks, std::map<double, double>& bids, bool saveMessages = true) {
        this->initialSnapshot = *new ImmutableOrderBookSnapshot(asks, bids);
        this->asks = asks;
        this->bids = bids;
        this->saveMessages = saveMessages;
    }

    OrderBookSnapshot(AbsOrderBookSnapshot& initialSnapshot) : OrderBookSnapshot(initialSnapshot.getAsks(), initialSnapshot.getBids()) {}
private:
    bool saveMessages;
    std::map<double, OrderBookDelta> deltas;
    std::map<double, double> asks;
    std::map<double, double> bids;
    ImmutableOrderBookSnapshot initialSnapshot = *new ImmutableOrderBookSnapshot();
};

#endif