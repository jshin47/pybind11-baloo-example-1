#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include <vector>

#include "definitions.h"
#include "OrderDirection.h"
#include "OrderBookDelta.h"
#include "ImmutableOrderBookSnapshot.h"
#include "OrderBookSnapshot.h"

PYBIND11_MODULE(baloo, m) {
    py::enum_<OrderDirection::OrderDirectionEnum>(m, "OrderDirection")
        .value("Ask", OrderDirection::Ask)
        .value("Bid", OrderDirection::Bid)
    ;

    py::class_<OrderBookDelta>(m, "OrderBookDelta")
        .def(py::init<>())
        .def(py::init<double, double, double, OrderDirection::OrderDirectionEnum>(), py::arg("timestamp"), py::arg("price"), py::arg("quantity"), py::arg("direction"))
        .def_property("timestamp", &OrderBookDelta::getTimestamp, &OrderBookDelta::setTimestamp)
        .def_property("price", &OrderBookDelta::getPrice, &OrderBookDelta::setPrice)
        .def_property("quantity", &OrderBookDelta::getQuantity, &OrderBookDelta::setQuantity)
        .def_property("direction", &OrderBookDelta::getDirection, &OrderBookDelta::setDirection)
    ;

    py::class_<ImmutableOrderBookSnapshot>(m, "ImmutableOrderBookSnapshot")
        .def(py::init<>())
        .def(py::init<std::map<double, double>&, std::map<double, double>&, double>(), py::arg("asks"), py::arg("bids"), py::arg("timestamp") = 0)
        .def_property_readonly("asks", &ImmutableOrderBookSnapshot::getAsks)
        .def_property_readonly("bids", &ImmutableOrderBookSnapshot::getBids)
        .def_property_readonly("timestamp", &ImmutableOrderBookSnapshot::getTimestamp)
    ;

    py::class_<OrderBookSnapshot>(m, "OrderBookSnapshot")
        .def(py::init<bool>(), py::arg("save_messages") = true)
        .def(py::init<std::map<double, double>&, std::map<double, double>&, bool>(), py::arg("asks"), py::arg("bids"), py::arg("save_messages") = true)
        .def("apply", (void (OrderBookSnapshot::*)(OrderBookDelta &)) &OrderBookSnapshot::apply, "Applies a single order book delta")
        .def("apply", (void (OrderBookSnapshot::*)(std::vector<OrderBookDelta> &)) &OrderBookSnapshot::apply, "Applies a list of order book deltas")
        .def("apply", (void (OrderBookSnapshot::*)(double, double, double, OrderDirection::OrderDirectionEnum)) &OrderBookSnapshot::apply, "Applies a single order book delta by values")
        .def("apply", (void (OrderBookSnapshot::*)(std::vector<std::tuple<double, double, double, OrderDirection::OrderDirectionEnum>>&)) &OrderBookSnapshot::apply, "Applies a list of order book delta tuples by values")
        .def("apply", (void (OrderBookSnapshot::*)(std::vector<double>&)) &OrderBookSnapshot::apply, "Applies a 3 * n element list of n deltas, with format timestamp price signed_quantity")
        .def("apply", (void (OrderBookSnapshot::*)(std::map<double, double>&, std::map<double, double>&)) &OrderBookSnapshot::apply, "Rewrites snapshot with new asks and bids")
        .def("get_snapshot_at_point_in_time", &OrderBookSnapshot::getSnapshotAtPointInTime, py::return_value_policy::take_ownership, "Gets a new snapshot at a point in time")
        .def("calculate_bid_ask_differential_bins", &OrderBookSnapshot::calculateBidAskDifferentialBins, py::return_value_policy::take_ownership, py::arg("bins"), py::arg("mode") = 1, "Calculates the bid-ask spread by bins")
        .def("apply_and_bucket", &OrderBookSnapshot::applyAndBucket, py::return_value_policy::take_ownership, py::arg("updates"), py::arg("time_buckets"), py::arg("bins"), py::arg("ignore_deltas_before_beginning_of_first_bin") = true, py::arg("calculate_bid_ask_spread_features") = true, "Calculates the bid-ask spread over time buckets")
        .def_property_readonly("asks", &OrderBookSnapshot::getAsks)
        .def_property_readonly("bids", &OrderBookSnapshot::getBids)
    ;

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}