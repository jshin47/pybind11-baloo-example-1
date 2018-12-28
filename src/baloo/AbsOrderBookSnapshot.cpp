#include "AbsOrderBookSnapshot.h"

namespace AbsOrderBookSnapshot_Private {



}

void AbsOrderBookSnapshot::calculateDifferentialsForBin(std::vector<double>& bins, std::vector<double>& binsValues, std::map<double, double>& priceMap, OrderDirection::OrderDirectionEnum direction) {
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

std::vector<double>& AbsOrderBookSnapshot::calculateBidAskDifferentialBins(std::vector<double>& bins) {
    std::vector<double>& binsValues = *new std::vector<double>(bins.size() - 1, 0);

    calculateDifferentialsForBin(bins, binsValues, getAsks(), OrderDirection::Ask);
    calculateDifferentialsForBin(bins, binsValues, getBids(), OrderDirection::Bid);
    
    return binsValues;
}
