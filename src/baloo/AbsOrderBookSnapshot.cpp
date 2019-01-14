#include "AbsOrderBookSnapshot.h"

#include <algorithm>

bool AbsOrderBookSnapshot::applyBinValueForPriceMapIterator(std::vector<double>& bins, std::vector<double>& binsValues, OrderDirection::OrderDirectionEnum direction, std::pair<double, double> elem) {
    bool biggerThanOrEqualToSmallestBinElement = elem.first >= bins[0];
    bool smallerThanBiggestBinElement = elem.first < bins[bins.size() - 1];
    bool withinSomeBin = biggerThanOrEqualToSmallestBinElement && smallerThanBiggestBinElement;
    if (withinSomeBin) {
        auto whichBin = std::upper_bound(bins.begin(), bins.end(), elem.first);
        int position = whichBin - bins.begin() - 1;
        binsValues[position] = binsValues[position] + ((direction == OrderDirection::Ask) ? -1 : 1) * elem.second;
        return true;
    } else if (direction == OrderDirection::Ask && !smallerThanBiggestBinElement) {
        return false;
    } else if (direction == OrderDirection::Bid && !biggerThanOrEqualToSmallestBinElement) {
        return false;
    }

    return true;
}

void AbsOrderBookSnapshot::calculateDifferentialsForBin(std::vector<double>& bins, std::vector<double>& binsValues, std::map<double, double>& priceMap, OrderDirection::OrderDirectionEnum direction) {
    int multiplier = (direction == OrderDirection::Ask) ? -1 : 1;
    
    if (direction == OrderDirection::Ask) {
        for (auto priceMapIterator = priceMap.begin(); priceMapIterator != priceMap.end(); ++priceMapIterator) {
            if (!applyBinValueForPriceMapIterator(bins, binsValues, direction, *priceMapIterator)) break;
        }
    } else if (direction == OrderDirection::Bid) {
        for (auto priceMapIterator = priceMap.rbegin(); priceMapIterator != priceMap.rend(); ++priceMapIterator) {
            if (!applyBinValueForPriceMapIterator(bins, binsValues, direction, *priceMapIterator)) break;
        }
    } else {
        throw "Cannot handle this order direction";
    }
}

std::vector<double>* AbsOrderBookSnapshot::calculateBidAskDifferentialBins(std::vector<double>& bins, unsigned int mode) {
    switch (mode) {
        case -1: {
            std::fill(binsValues.begin(), binsValues.end(), 0);
            binsValues.resize(bins.size() - 1, 0);

            calculateDifferentialsForBin(bins, binsValues, getAsks(), OrderDirection::Ask);
            calculateDifferentialsForBin(bins, binsValues, getBids(), OrderDirection::Bid);
            
            return &binsValues;
        }
        case 1:
        case 2: {
            std::vector<double>* binsV = new std::vector<double>(bins.size() - 1, 0);
            calculateDifferentialsForBin(bins, *binsV, getAsks(), OrderDirection::Ask);
            calculateDifferentialsForBin(bins, *binsV, getBids(), OrderDirection::Bid);
            return binsV;
        }
        default:
            throw "Error";
    }

    
}
