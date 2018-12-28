#include <pybind11/pybind11.h>

#ifndef __BALOO_ORDER_DIRECTION_H__
#define __BALOO_ORDER_DIRECTION_H__

namespace OrderDirection {
    enum OrderDirectionEnum {
        Ask,
        Bid,
    };
}

#endif