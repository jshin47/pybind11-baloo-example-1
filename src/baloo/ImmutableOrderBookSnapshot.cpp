#include "ImmutableOrderBookSnapshot.h"

double ImmutableOrderBookSnapshot::getTimestamp() {
    return timestamp;
}

std::map<double, double>& ImmutableOrderBookSnapshot::getAsks() {
    return asks;
}

std::map<double, double>& ImmutableOrderBookSnapshot::getBids() {
    return bids;
}