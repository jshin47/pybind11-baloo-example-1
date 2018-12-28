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
    OrderDirection::OrderDirectionEnum getDirection();
    void setDirection(OrderDirection::OrderDirectionEnum direction);

    OrderBookDelta() {}

    OrderBookDelta(TimeType& timestamp, double price, double quantity, OrderDirection::OrderDirectionEnum direction) {
        this->timestamp = timestamp;
        this->price = price;
        this->quantity = quantity;
        this->direction = direction;
    }
private:
    TimeType timestamp;
    double price;
    double quantity;
    OrderDirection::OrderDirectionEnum direction;
};

#endif
