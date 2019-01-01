# Instructions

 - `git clone --recursive https://github.com/jshin47/pybind11-baloo-example-1`
 - `pip3 install pytest`
 - `python3 setup.py install`
 - `python3 test/smoketest/baloo.smoketest.py`
 - `pytest -s test/pytest/OrderBookSnapshot.py`

     for (int i = 0; i < timeBuckets.size() - 1; i++) {
        double timeBucketStart = timeBuckets[i];
        double timeBucketEnd = timeBuckets[i + 1];
        
        auto leftDelta = deltasMap.lower_bound(timeBucketStart);
        auto rightDelta = deltasMap.lower_bound(timeBucketEnd);
        for (auto deltaIterator = leftDelta; deltaIterator != rightDelta; ++deltaIterator) {
            apply(deltaIterator->second);
            lastDeltaPosition = deltaIterator;
        }
        if (i > 0) {
            buckets_list[i - 1] = calculateBidAskDifferentialBins(bins);
        }
    }