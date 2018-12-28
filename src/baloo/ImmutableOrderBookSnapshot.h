#ifndef __BALOO_IMMUTABLE_ORDERBOOK_SNAPSHOT_H__
#define __BALOO_IMMUTABLE_ORDERBOOK_SNAPSHOT_H__

#include <vector>
#include <map>
#include <string>

#include "definitions.h"

#include "AbsOrderBookSnapshot.h"

class ImmutableOrderBookSnapshot : public AbsOrderBookSnapshot {
public:
    std::map<double, double>& getAsks();
    std::map<double, double>& getBids();

    ImmutableOrderBookSnapshot() {}

    ImmutableOrderBookSnapshot(std::map<double, double>& asks, std::map<double, double>& bids) {
        this->asks = *new std::map<double, double>(asks);
        this->bids = *new std::map<double, double>(bids);
    }

    static ImmutableOrderBookSnapshot emptySnapshot;

    static ImmutableOrderBookSnapshot getEmptySnapshot() { return emptySnapshot; }
private:
    std::map<double, double> asks;
    std::map<double, double> bids;
};

#endif