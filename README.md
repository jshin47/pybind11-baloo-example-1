[![Build Status](https://travis-ci.org/jshin47/pybind11-baloo-example-1.svg?branch=master)](https://travis-ci.org/jshin47/pybind11-baloo-example-1)

# Getting Started

 - `git clone --recursive https://github.com/jshin47/pybind11-baloo-example-1`

## Local Instructions

 - `pip3 install pytest`
 - `python3 setup.py install`
 - `pytest -s test/pytest/OrderBookSnapshot.py`
 - `python3 test/smoketest/baloo.smoketest.py` - if you want to run the old tests

# Docker Instructions

 - `docker build -t "baloo-snapshot" .`
 - `docker run baloo-snapshot` - runs more than 400 pytest tests
