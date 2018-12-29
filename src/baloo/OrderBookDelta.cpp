#include "OrderBookDelta.h"

double OrderBookDelta::getTimestamp() {
    return timestamp;
}

void OrderBookDelta::setTimestamp(double timestamp) {
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

OrderDirection::OrderDirectionEnum OrderBookDelta::getDirection() {
    return direction;
}

void OrderBookDelta::setDirection(OrderDirection::OrderDirectionEnum direction) {
    this->direction = direction;
}