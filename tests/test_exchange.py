from project.exchange import StockExchange
from project.enums import Side, OrderType, OrderStatus


def test_limit_buy_added_to_book_when_no_match():
    exchange = StockExchange()

    order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    book = exchange.exchange[order.stock_name]

    level = book.bids[order.price]

    assert book.bids[order.price] == [order]
    assert order in level
    assert len(level) == 1
    assert order.filled_quantity == 0
    assert order.status == OrderStatus.PENDING


def test_limit_buy_fully_filled_when_matching_sell_exists():
    exchange = StockExchange()

    order_sell = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    order_buy = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    book = exchange.exchange[order_buy.stock_name]

    assert order_buy.status == OrderStatus.FILLED
    assert order_sell.status == OrderStatus.FILLED
    assert order_buy.filled_quantity == 10
    assert order_sell.filled_quantity == 10
    assert book.bids == {}
    assert book.asks == {}


def test_limit_sell_partially_filled_when_buy_quantity_is_smaller():
    exchange = StockExchange()

    order_buy = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    order_sell = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=20,
    )

    book = exchange.exchange[order_sell.stock_name]
    level = book.asks[order_sell.price]

    assert order_buy.status == OrderStatus.FILLED
    assert order_sell.status == OrderStatus.PARTIAL
    assert order_sell.filled_quantity == 10
    assert order_sell.quantity - order_sell.filled_quantity == 10
    assert book.bids == {}
    assert level == [order_sell]


def test_limit_buy_matches_multiple_sell_orders():
    exchange = StockExchange()

    sell_order1 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    sell_order2 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    buy_order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book = exchange.exchange[buy_order.stock_name]

    assert sell_order1.status == OrderStatus.FILLED
    assert sell_order2.status == OrderStatus.FILLED
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order1.filled_quantity == 5
    assert sell_order2.filled_quantity == 5
    assert buy_order.filled_quantity == 10
    assert book.bids == {}
    assert book.asks == {}


def test_limit_buy_partially_matches_multiple_sell_orders():
    exchange = StockExchange()

    sell_order1 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    sell_order2 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    buy_order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=15,
    )

    book = exchange.exchange[buy_order.stock_name]
    level = book.bids[buy_order.price]

    assert sell_order1.status == OrderStatus.FILLED
    assert sell_order2.status == OrderStatus.FILLED
    assert buy_order.status == OrderStatus.PARTIAL
    assert sell_order1.filled_quantity == 5
    assert sell_order2.filled_quantity == 5
    assert buy_order.filled_quantity == 10
    assert buy_order.quantity - buy_order.filled_quantity == 5
    assert buy_order.execution_price == 100
    assert book.asks == {}
    assert level == [buy_order]


def test_last_price_updated_after_trade():
    exchange = StockExchange()

    sell_order = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book = exchange.exchange[sell_order.stock_name]

    assert book.last_price is None

    buy_order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    assert book.last_price == buy_order.price


def test_last_price_updates_after_multiple_trades():
    exchange = StockExchange()

    sell_order = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )

    book = exchange.exchange[sell_order.stock_name]

    assert book.last_price is None

    buy_order1 = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )

    assert book.last_price == buy_order1.price

    buy_order2 = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=5,
    )

    assert book.last_price == 100
    assert buy_order2.execution_price == 100


def test_market_buy_executes_immediately_against_best_ask():
    exchange = StockExchange()

    sell_order = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=10,
    )
    book = exchange.exchange[sell_order.stock_name]

    buy_order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.MKT,
        price=None,
        quantity=10,
    )

    assert sell_order.status == OrderStatus.FILLED
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order.filled_quantity == 10
    assert buy_order.filled_quantity == 10
    assert buy_order.execution_price == 100
    assert book.last_price == 100
    assert book.last_price == sell_order.execution_price
    assert book.bids == {}
    assert book.asks == {}


def test_market_buy_consumes_multiple_price_levels():
    exchange = StockExchange()

    sell_order1 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )
    sell_order2 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=10,
    )
    book = exchange.exchange[sell_order1.stock_name]

    buy_order = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.MKT,
        price=None,
        quantity=10,
    )

    level = book.asks[101]

    assert sell_order1.status == OrderStatus.FILLED
    assert sell_order2.status == OrderStatus.PARTIAL
    assert buy_order.status == OrderStatus.FILLED
    assert sell_order1.filled_quantity == 5
    assert sell_order2.filled_quantity == 5
    assert sell_order2.quantity - sell_order2.filled_quantity == 5
    assert buy_order.filled_quantity == 10
    assert book.last_price == sell_order2.price
    assert buy_order.execution_price in (100, 101)
    assert sell_order2 in level
    assert level == [sell_order2]


def test_exchange_end_to_end_matching_flow():
    exchange = StockExchange()

    # --- build initial liquidity ---
    sell1 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=100,
        quantity=5,
    )

    sell2 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=101,
        quantity=10,
    )

    sell3 = exchange.place_order(
        side=Side.SELL,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=102,
        quantity=5,
    )

    book = exchange.exchange["AAPL"]

    # initial state
    assert book.last_price is None

    # --- MARKET BUY consumes multiple levels ---
    buy1 = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.MKT,
        price=None,
        quantity=12,
    )

    # should fill
    # 5 @100
    # 7 @101 (partial)
    assert sell1.status == OrderStatus.FILLED
    assert sell2.status == OrderStatus.PARTIAL
    assert sell3.status == OrderStatus.PENDING

    assert buy1.status == OrderStatus.FILLED
    assert buy1.filled_quantity == 12

    # last trade should be from second level
    assert book.last_price == 101

    # book consistensy
    assert book.bids == {}

    assert book.asks[101] == [sell2]
    assert book.asks[102] == [sell3]
    assert sell2.filled_quantity == 7
    assert sell2.quantity - sell2.filled_quantity == 3

    # --- LIMIT BUY consumes remaining liquidity ---
    buy2 = exchange.place_order(
        side=Side.BUY,
        stock_name="AAPL",
        type_order=OrderType.LMT,
        price=102,
        quantity=10,
    )

    # should finish remaining
    assert sell1.status == OrderStatus.FILLED
    assert sell2.status == OrderStatus.FILLED
    assert sell3.status == OrderStatus.FILLED
    assert buy2.status == OrderStatus.PARTIAL

    level = book.bids[102]

    # final cleanup
    assert book.asks == {}
    assert buy2.filled_quantity == 8
    assert buy2.quantity - buy2.filled_quantity == 2
    assert level == [buy2]

    # last price should bi from final match
    assert book.last_price == 102
