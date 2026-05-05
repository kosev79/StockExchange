from project.order import Order
from project.order_book import OrderBook
from project.matching_engine import MatchEngine
from project.enums import Side, OrderType, OrderStatus

COMMANDS = {"BUY", "SELL", "VIEW", "QUOTE", "QUIT", "BOOK"}


class StockExchange:
    def __init__(self):
        self.exchange = {}
        self.orders = {}
        self.next_order_id = 1
        self.engine = MatchEngine()

    def place_order(self, side, stock_name, type_order, price, quantity):
        order = Order(
            id=self.next_order_id,
            side=side,
            stock_name=stock_name,
            type_order=type_order,
            price=price,
            quantity=quantity,
        )
        self.orders[self.next_order_id] = order
        if stock_name not in self.exchange:
            self.exchange[stock_name] = OrderBook()
        order_book = self.exchange[stock_name]
        order_book.add_order(order)
        self.engine.match(order_book, order)

        self.next_order_id += 1
        return order

    def validate_command(self, command):
        parts = command.split()
        if not parts:
            return False, "Invalid command"

        if parts[0] not in COMMANDS:
            return False, "Invalid command"

        if parts[0] == "VIEW":
            if len(parts) != 2 or parts[1] != "ORDERS":
                return False, "User orders format: VIEW ORDERS"

        if parts[0] == "QUOTE" and len(parts) != 2:
            return False, "Quote format: QUOTE <stock_name>"

        if parts[0] == "QUIT" and len(parts) != 1:
            return False, "QUIT command does not take any arguments"

        if parts[0] == "BOOK" and len(parts) != 2:
            return False, "Book format: BOOK <stock_name>"

        if parts[0] in ("BUY", "SELL"):
            if len(parts) < 4:
                return False, "Invalid command"

            if parts[2] not in ("MKT", "LMT"):
                return False, "Invalid order type, must be MKT or LMT"

            stock = parts[1]
            if not stock.isalpha() or not stock.isupper():
                return False, "Stock name must be alphabetic and uppercase"

            if parts[2] == "MKT":
                if len(parts) != 4:
                    return (
                        False,
                        "Market order format: BUY|SELL <stock_name> MKT <quantity>",
                    )
                try:
                    quantity = int(parts[3])
                    if quantity <= 0:
                        return False, "Quantity must be a positive integer"
                except ValueError:
                    return False, "Invalid quantity"

            if parts[2] == "LMT":
                if len(parts) != 5:
                    return (
                        False,
                        "Limit order format: BUY|SELL <stock_name> LMT $<price> <quantity>",
                    )
                try:
                    float(parts[3].replace("$", ""))
                except ValueError:
                    return False, "Invalid price"
                try:
                    quantity = int(parts[4])
                    if quantity <= 0:
                        return False, "Quantity must be a positive integer"
                except ValueError:
                    return False, "Invalid quantity"
        return True, None

    def process_command(self, command):
        parts = command.split()

        if parts[0] in ("BUY", "SELL"):
            side = Side(parts[0])
            stock_name = parts[1]
            type_order = OrderType(parts[2])
            if type_order == OrderType.MKT:
                price = None
                quantity = int(parts[3])
            else:
                price = float(parts[3].replace("$", ""))
                quantity = int(parts[4])
            order = self.place_order(side, stock_name, type_order, price, quantity)
            return order

        elif parts[0] == "VIEW":
            return self.get_orders()

        elif parts[0] == "QUOTE":
            stock_name = parts[1]
            return self.quote(stock_name)

        elif parts[0] == "BOOK":
            stock_name = parts[1]
            if stock_name in self.exchange:
                print(self.exchange[stock_name])
            else:
                print(f"No data for {stock_name}")

    def get_orders(self):
        return " ".join(repr(order) for order in self.orders.values())

    def quote(self, stock_name):
        if stock_name in self.exchange:
            order_book = self.exchange[stock_name]
            best_bid = order_book.best_bid()
            best_ask = order_book.best_ask()
            last_price = order_book.last_price
            bid_str = (
                f"BID: ${best_bid.price:.2f}"
                if best_bid and best_bid.price is not None
                else "BID: N/A"
            )
            ask_str = (
                f"ASK: ${best_ask.price:.2f}"
                if best_ask and best_ask.price is not None
                else "ASK: N/A"
            )
            last_price_str = (
                f"LAST: ${last_price:.2f}" if last_price is not None else "LAST: N/A"
            )
            return f"{stock_name} {bid_str} {ask_str} {last_price_str}"
        else:
            return f"No data for {stock_name}"
