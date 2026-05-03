from src.project.order import Order
from src.project.order_book import OrderBook
from src.project.enums import Side, OrderType, OrderStatus
from src.project.matching_engine import MatchEngine


def test_limit_orders_full_fill():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.FILLED
    assert buy_order.filled_quantity == 10
    assert sell_order.filled_quantity == 10


def test_limit_orders_partial_fill():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.PARTIAL
    assert sell_order.filled_quantity == 10


def test_order_remove_after_fill():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    # оба исполнены
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.FILLED

    # главное: из книги изчезли
    all_bids = [o for orders in book.bids.values() for o in orders]
    all_asks = [o for orders in book.asks.values() for o in orders]

    assert buy_order not in all_bids
    assert sell_order not in all_asks


def test_order_remove_after_partial_fill():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.PARTIAL
    assert sell_order.filled_quantity == 10


def test_price_rejecrs_no_match():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=90,
        quantity=10,
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    book.add_order(buy_order)
    engine.match(book, sell_order)

    assert buy_order.status == OrderStatus.PENDING
    assert sell_order.status == OrderStatus.PENDING
    assert buy_order.filled_quantity == 0


def test_market_buy_matches_limit_sell():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1, side=Side.BUY, stock_name="AAPL", type_order=OrderType.MKT, quantity=10
    )

    sell_order = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    # факт сделки
    assert buy_order.filled_quantity == 10
    assert sell_order.filled_quantity == 10

    # статус
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.FILLED

    # цена сделки
    assert buy_order.execution_price == 100
    assert sell_order.execution_price == 100


def test_limit_buy_matches_market_sell():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    sell_order = Order(
        id=2, side=Side.BUY, stock_name="AAPL", type_order=OrderType.MKT, quantity=10
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    # факт сделки
    assert buy_order.filled_quantity == 10
    assert sell_order.filled_quantity == 10

    # статус
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.status == OrderStatus.FILLED

    # цена сделки
    assert buy_order.execution_price == 100
    assert sell_order.execution_price == 100


def test_no_match_market_order():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1, side=Side.BUY, stock_name="AAPL", type_order=OrderType.MKT, quantity=10
    )
    sell_order = Order(
        id=2, side=Side.SELL, stock_name="AAPL", type_order=OrderType.MKT, quantity=10
    )

    book.add_order(buy_order)
    engine.match(book, sell_order)

    # ничего не исполнено
    assert buy_order.filled_quantity == 0
    assert sell_order.filled_quantity == 0

    # статус не изменился
    assert buy_order.status == OrderStatus.PENDING
    assert sell_order.status == OrderStatus.PENDING

    # цена не выставлена
    assert buy_order.execution_price is None
    assert sell_order.execution_price is None

    # важно: книга не должна быть изменена через match
    assert buy_order in book.bids.get(None, [])


def test_price_priority_best_price_executes_first():
    book = OrderBook()
    engine = MatchEngine()

    buy1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    buy2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=10,
    )
    sell = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy1)
    book.add_order(buy2)
    engine.match(book, sell)

    assert buy2.status == OrderStatus.FILLED
    assert buy1.status == OrderStatus.PENDING


def test_fifo_with_same_price():
    book = OrderBook()
    engine = MatchEngine()

    buy1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    buy2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    sell = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )

    book.add_order(buy1)
    book.add_order(buy2)
    engine.match(book, sell)

    assert buy1.status == OrderStatus.FILLED
    assert buy2.status == OrderStatus.PENDING


def test_multi_match_across_muliple_orders():
    book = OrderBook()
    engine = MatchEngine()

    buy1 = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    buy2 = Order(
        id=2,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    sell = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy1)
    book.add_order(buy2)
    engine.match(book, sell)

    assert buy1.status == OrderStatus.FILLED
    assert buy2.status == OrderStatus.FILLED
    assert sell.status == OrderStatus.FILLED


def test_buy_order_matches_multiple_sell_orders():
    book = OrderBook()
    engine = MatchEngine()

    buy_order = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=40,
    )
    sell1 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )
    sell2 = Order(
        id=3,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    sell3 = Order(
        id=4,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy_order)
    engine.match(book, sell1)
    engine.match(book, sell2)
    engine.match(book, sell3)

    assert buy_order.status == OrderStatus.FILLED
    assert sell1.status == OrderStatus.FILLED
    assert sell2.status == OrderStatus.FILLED
    assert sell3.status == OrderStatus.FILLED


def test_last_price_updates_after_trade():
    book = OrderBook()
    engine = MatchEngine()

    buy = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy)
    engine.match(book, sell)

    assert book.last_price == 100


def test_last_price_not_updated_when_no_match():
    book = OrderBook()
    engine = MatchEngine()

    buy = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=90,
        quantity=10,
    )

    sell = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book.add_order(buy)
    engine.match(book, sell)

    assert book.last_price is None


def test_last_price_reflects_last_trade_in_sequence():
    book = OrderBook()
    engine = MatchEngine()

    sell1 = Order(
        id=1,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )

    sell2 = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=5,
    )

    buy = Order(
        id=3, side=Side.BUY, stock_name="AAPL", type_order=OrderType.MKT, quantity=10
    )

    book.add_order(sell1)
    book.add_order(sell2)

    engine.match(book, buy)

    assert book.last_price == 101


def test_last_price_updates_on_partial_fill():
    book = OrderBook()
    engine = MatchEngine()

    buy = Order(
        id=1,
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    sell = Order(
        id=2,
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book.add_order(buy)
    engine.match(book, sell)

    assert book.last_price == 100
