from src.project.order import Order
from src.project.enums import Side, OrderType, OrderStatus
import pytest


def test_order_initial_status():
    order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    assert order.status == OrderStatus.PENDING


def test_order_partial():
    order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
        filled_quantity=5,
    )
    order.update_status()
    assert order.status == OrderStatus.PARTIAL


def test_order_filled():
    order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
        filled_quantity=10,
    )
    order.update_status()
    assert order.status == OrderStatus.FILLED


def test_market_order_price_is_none():
    order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.MKT,
        price=100,
        quantity=10,
    )
    assert order.price is None


def test_order_zero_filled_is_pending():
    order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
        filled_quantity=0,
    )
    order.update_status()
    assert order.status == OrderStatus.PENDING


def test_order_zero_qyantity_raises():
    with pytest.raises(ValueError):
        Order(
            id=1,
            side=Side.BUY,
            stock_name="AAPL",
            type_order=OrderType.LMT,
            price=100,
            quantity=0,
        )


def test_filled_greater_than_quantity_raises():
    with pytest.raises(ValueError):
        Order(
            id=1,
            side=Side.BUY,
            stock_name="AAPL",
            type_order=OrderType.LMT,
            price=100,
            quantity=10,
            filled_quantity=20,
        )


def test_negative_filled_quantity_raises():
    with pytest.raises(ValueError):
        Order(
            id=1,
            side=Side.BUY,
            stock_name="AAPL",
            type_order=OrderType.LMT,
            price=100,
            quantity=10,
            filled_quantity=-1,
        )
