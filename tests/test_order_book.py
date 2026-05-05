from project import order
from project.order import Order
from project.order_book import OrderBook
from project.enums import Side, OrderType


def test_add_buy_order_to_bids():
    book = OrderBook()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)

    assert book.bids == {buy_order.price: [buy_order]}


def test_add_sell_order_to_asks():
    book = OrderBook()

    sell_order = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(sell_order)
    level = book.asks[sell_order.price]

    assert sell_order.price in book.asks
    assert sell_order in level
    assert len(level) == 1
    assert book.bids == {}


def test_add_orders_group_by_price():
    book = OrderBook()

    price = 100

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=price,
        quantity=10,
    )

    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=price,
        quantity=15,
    )

    book.add_order(buy_order1)
    book.add_order(buy_order2)

    assert price in book.bids
    assert len(book.bids) == 1

    level = book.bids[price]

    assert len(level) == 2
    assert level == [buy_order1, buy_order2]


def test_remove_order_from_book():
    book = OrderBook()

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=15,
    )

    price = buy_order1.price

    book.add_order(buy_order1)
    book.add_order(buy_order2)

    book.remove_order(buy_order1.side, buy_order1)

    level = book.bids[price]

    assert buy_order1 not in level
    assert buy_order2 in level
    assert len(level) == 1


def test_remove_order_deletes_price_level_when_empty():
    book = OrderBook()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)

    book.remove_order(buy_order.side, buy_order)

    assert book.bids == {}


def test_remove_order_does_not_affect_other_price_levels():
    book = OrderBook()

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=10,
    )

    book.add_order(buy_order1)
    book.add_order(buy_order2)

    book.remove_order(buy_order1.side, buy_order1)

    assert len(book.bids) == 1
    assert list(book.bids.keys()) == [buy_order2.price]


def test_best_bid_returns_highest_price():
    book = OrderBook()

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    buy_order3 = Order(
        id=3,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=103,
        quantity=20,
    )

    book.add_order(buy_order1)
    book.add_order(buy_order2)
    book.add_order(buy_order3)

    assert book.best_bid() == buy_order2


def test_best_ask_returns_lowest_price():
    book = OrderBook()

    sell_order1 = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=102,
        quantity=10,
    )
    sell_order2 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    sell_order3 = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=20,
    )

    book.add_order(sell_order1)
    book.add_order(sell_order2)
    book.add_order(sell_order3)

    assert book.best_ask() == sell_order3


def test_best_bid_returns_first_order_on_same_price():
    book = OrderBook()

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    buy_order3 = Order(
        id=3,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=20,
    )

    book.add_order(buy_order1)
    book.add_order(buy_order2)
    book.add_order(buy_order3)

    best = book.best_bid()

    assert best == buy_order2
    assert best.price == 105


def test_best_ask_returns_first_order_on_same_price():
    book = OrderBook()

    sell_order1 = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    sell_order2 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    sell_order3 = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book.add_order(sell_order1)
    book.add_order(sell_order2)
    book.add_order(sell_order3)

    best = book.best_ask()

    assert best == sell_order1
    assert best.price == 100


def test_best_bid_updates_after_removal():
    book = OrderBook()

    buy_order1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    buy_order3 = Order(
        id=3,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=20,
    )

    book.add_order(buy_order1)
    book.add_order(buy_order2)
    book.add_order(buy_order3)
    book.remove_order(buy_order2.side, buy_order2)

    best = book.best_bid()

    assert best.price == 105
    assert best == buy_order3
    assert 105 in book.bids


def test_best_ask_updates_after_removal():
    book = OrderBook()

    sell_order1 = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    sell_order2 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=15,
    )
    sell_order3 = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book.add_order(sell_order1)
    book.add_order(sell_order2)
    book.add_order(sell_order3)
    book.remove_order(sell_order1.side, sell_order1)

    best = book.best_ask()

    assert best.price == 100
    assert best == sell_order3
    assert 100 in book.asks


def test_best_bid_returns_none_when_empty():
    book = OrderBook()
    assert book.best_bid() is None


def test_best_ask_returns_none_when_empty():
    book = OrderBook()
    assert book.best_ask() is None


def test_get_opposite_buy_returns_best_ask():
    book = OrderBook()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    sell_order1 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=99,
        quantity=10,
    )
    sell_order2 = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=98,
        quantity=10,
    )

    book.add_order(buy_order)
    book.add_order(sell_order1)
    book.add_order(sell_order2)

    best_ask = book.best_ask()
    opposite, side = book.get_opposite(buy_order)

    assert opposite == best_ask
    assert side == Side.SELL
    assert opposite.price == 98


def test_get_opposite_sell_returns_best_bid():
    book = OrderBook()

    sell_order = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy_order1 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=103,
        quantity=10,
    )
    buy_order2 = Order(
        id=3,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=105,
        quantity=10,
    )

    book.add_order(sell_order)
    book.add_order(buy_order1)
    book.add_order(buy_order2)

    best_bid = book.best_bid()
    opposite, side = book.get_opposite(sell_order)

    assert opposite == best_bid
    assert side == Side.BUY
    assert opposite.price == 105


def test_get_opposite_returns_none_when_empty():
    book = OrderBook()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)

    opposite, side = book.get_opposite(buy_order)

    assert opposite is None
    assert side == Side.SELL
