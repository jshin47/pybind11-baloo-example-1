#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include <vector>

#include "definitions.h"
#include "OrderDirection.h"
#include "OrderBookDelta.h"
#include "OrderBookSnapshot.h"

PYBIND11_MODULE(baloo, m) {
    py::enum_<OrderDirection>(m, "OrderDirection")
        .value("Ask", OrderDirection::Ask)
        .value("Bid", OrderDirection::Bid)
    ;

    py::class_<OrderBookDelta>(m, "OrderBookDelta")
        .def(py::init<>())
        .def(py::init<TimeType&, double, double, OrderDirection>(), py::arg("timestamp"), py::arg("price"), py::arg("quantity"), py::arg("direction"))
        .def_property("timestamp", &OrderBookDelta::getTimestamp, &OrderBookDelta::setTimestamp)
        .def_property("price", &OrderBookDelta::getPrice, &OrderBookDelta::setPrice)
        .def_property("quantity", &OrderBookDelta::getQuantity, &OrderBookDelta::setQuantity)
        .def_property("direction", &OrderBookDelta::getDirection, &OrderBookDelta::setDirection)
    ;

    py::class_<OrderBookSnapshot>(m, "OrderBookSnapshot")
        .def(py::init<>())
        .def("apply", (void (OrderBookSnapshot::*)(OrderBookDelta &)) &OrderBookSnapshot::apply, "Applies a single order book delta")
        .def("apply", (void (OrderBookSnapshot::*)(std::vector<OrderBookDelta> &)) &OrderBookSnapshot::apply, "Applies a list of order book deltas")
        .def("get_snapshot_at_point_in_time", &OrderBookSnapshot::getSnapshotAtPointInTime, py::return_value_policy::take_ownership, "Gets a new snapshot at a point in time")
        .def_property_readonly("asks", &OrderBookSnapshot::getAsks)
        .def_property_readonly("bids", &OrderBookSnapshot::getBids)
    ;

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}