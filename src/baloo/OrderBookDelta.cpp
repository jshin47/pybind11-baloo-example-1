#include "OrderBookDelta.h"

TimeType& OrderBookDelta::getTimestamp() {
    return timestamp;
}

void OrderBookDelta::setTimestamp(TimeType& timestamp) {
    this->timestamp = timestamp;
}

double OrderBookDelta::getPrice() {
    return price;
}

void OrderBookDelta::setPrice(double price) {
    this->price = price;
}

double OrderBookDelta::getQuantity() {
    return quantity;
}

void OrderBookDelta::setQuantity(double quantity) {
    this->quantity = quantity;
}

OrderDirection OrderBookDelta::getDirection() {
    return direction;
}

void OrderBookDelta::setDirection(OrderDirection direction) {
    this->direction = direction;
}