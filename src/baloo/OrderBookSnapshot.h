#ifndef __BALOO_ORDERBOOK_SNAPSHOT_H__
#define __BALOO_ORDERBOOK_SNAPSHOT_H__

#include <vector>
#include <map>
#include <chrono>
#include <string>

#include "definitions.h"
#include "OrderBookDelta.h"

class OrderBookSnapshot {
public:
    void apply(OrderBookDelta &delta);
    void apply(std::vector<OrderBookDelta> &deltas);
    OrderBookSnapshot& getSnapshotAtPointInTime(TimeType& pointInTime);
    std::vector<double>& calculateBidAskDifferentialBins(std::vector<double> &bins);

    std::map<TimeType, OrderBookDelta> getDeltas();
    std::map<double, double> getAsks();
    std::map<double, double> getBids();
private:
    std::map<TimeType, OrderBookDelta> deltas;
    std::map<double, double> asks;
    std::map<double, double> bids;
};

#endif