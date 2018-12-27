#ifndef __BALOO_ORDERBOOK_DELTA_H__
#define __BALOO_ORDERBOOK_DELTA_H__

#include <chrono>

#include "definitions.h"
#include "OrderDirection.h"

class OrderBookDelta {
public:
    TimeType& getTimestamp();
    void setTimestamp(TimeType& timestamp);
    double getPrice();
    void setPrice(double price);
    double getQuantity();
    void setQuantity(double quantity);
    OrderDirection getDirection();
    void setDirection(OrderDirection direction);
private:
    TimeType timestamp;
    double price;
    double quantity;
    OrderDirection direction;
};

#endif
