#include "ImmutableOrderBookSnapshot.h"

std::map<double, double>& ImmutableOrderBookSnapshot::getAsks() {
    return asks;
}

std::map<double, double>& ImmutableOrderBookSnapshot::getBids() {
    return bids;
}