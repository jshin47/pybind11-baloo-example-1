#ifndef __BALOO_ABS_ORDERBOOK_SNAPSHOT_H__
#define __BALOO_ABS_ORDERBOOK_SNAPSHOT_H__

#include <vector>
#include <map>
#include <string>

#include "definitions.h"

#include "OrderDirection.h"

class AbsOrderBookSnapshot {
public:
    std::vector<double>& calculateBidAskDifferentialBins(std::vector<double>& bins, unsigned int mode = 1);

    virtual std::map<double, double>& getAsks() = 0;
    virtual std::map<double, double>& getBids() = 0;
protected:
    bool applyBinValueForPriceMapIterator(std::vector<double>& bins, std::vector<double>& binsValues, OrderDirection::OrderDirectionEnum direction, std::pair<double, double> elem);
    void calculateDifferentialsForBin(std::vector<double>& bins, std::vector<double>& binsValues, std::map<double, double>& priceMap, OrderDirection::OrderDirectionEnum direction);
    std::vector<double> binsValues;
};

#endif