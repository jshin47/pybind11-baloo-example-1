#ifndef __BALOO_ORDERBOOK_SNAPSHOT_H__
#define __BALOO_ORDERBOOK_SNAPSHOT_H__

#include <vector>
#include <map>
#include <chrono>
#include <string>
#include <memory>

#include "definitions.h"
#include "AbsOrderBookSnapshot.h"
#include "ImmutableOrderBookSnapshot.h"
#include "OrderBookDelta.h"

class OrderBookSnapshot : public AbsOrderBookSnapshot {
public:
    void apply(OrderBookDelta& delta);
    void apply(std::vector<OrderBookDelta>& deltas);
    OrderBookSnapshot& getSnapshotAtPointInTime(TimeType& pointInTime);

    std::map<TimeType, OrderBookDelta>& getDeltas();
    std::map<double, double>& getAsks();
    std::map<double, double>& getBids();

    OrderBookSnapshot() { }

    OrderBookSnapshot(std::map<double, double>& asks, std::map<double, double>& bids) {
        this->initialSnapshot = *new ImmutableOrderBookSnapshot(asks, bids);
        this->asks = asks;
        this->bids = bids;
    }

    OrderBookSnapshot(AbsOrderBookSnapshot& initialSnapshot) : OrderBookSnapshot(initialSnapshot.getAsks(), initialSnapshot.getBids()) {
    }
private:
    std::map<TimeType, OrderBookDelta> deltas;
    std::map<double, double> asks;
    std::map<double, double> bids;
    ImmutableOrderBookSnapshot initialSnapshot = *new ImmutableOrderBookSnapshot();
};

#endif