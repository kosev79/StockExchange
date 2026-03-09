import time


COMMANDS = {"BUY", "SELL", "VIEW", "QUOTE", "QUIT", "BOOK"}


class Order:
    def __init__(self, id, side, stock_name, type_order, price=None, quantity=None):
        self.id = id
        self.side = side
        self.stock_name = stock_name
        self.type_order = type_order
        self.price = (
            price if type_order == "LMT" else (float("inf") if side == "BUY" else 0.0)
        )
        self.execution_price = None
        self.quantity = quantity
        self.filled_quantity = 0
        self.status = "PENDING"
        self.timestamp = time.time()

    def update_status(self):
        if self.filled_quantity == 0:
            self.status = "PENDING"
        elif self.filled_quantity < self.quantity:
            self.status = "PARTIAL"
        else:
            self.status = "FILLED"

    def __str__(self):
        if self.type_order == "LMT":
            if self.side == "SELL":
                return f"Вы разместили лимитный ордер на продажу {self.quantity} акций {self.stock_name} по цене ${self.price:.2f} за акцию."
            else:
                return f"Вы разместили лимитный ордер на покупку {self.quantity} акций {self.stock_name} по цене ${self.price:.2f} за акцию."
        else:
            if self.side == "SELL":
                return f"Вы разместили рыночный ордер на продажу {self.quantity} акций {self.stock_name}"
            else:
                return f"Вы разместили рыночный ордер на покупку {self.quantity} акций {self.stock_name}"

    def __repr__(self):
        if self.execution_price is not None:
            price_str = f" ${self.execution_price:.2f}"
        elif self.type_order == "LMT":
            price_str = f" ${self.price:.2f}"
        else:
            price_str = ""
        return (
            f"{self.id}. {self.stock_name} {self.type_order} {self.side}"
            f"{price_str} {self.filled_quantity}/{self.quantity} {self.status}"
        )


class OrderBook:
    def __init__(self):
        self.order_book = {"bids": {}, "asks": {}, "last_price": None}

    def add_order(self, order):
        book_side = "bids" if order.side == "BUY" else "asks"
        if order.price not in self.order_book[book_side]:
            self.order_book[book_side][order.price] = []
        self.order_book[book_side][order.price].append(order)

    def best_bids(self):
        if not self.order_book["bids"]:
            return None
        best_price = max(self.order_book["bids"].keys())
        return self.order_book["bids"][best_price][0]

    def best_asks(self):
        if not self.order_book["asks"]:
            return None
        best_price = min(self.order_book["asks"].keys())
        return self.order_book["asks"][best_price][0]

    def _trade_volume(self, incoming_order, resting_order):
        return min(
            incoming_order.quantity - incoming_order.filled_quantity,
            resting_order.quantity - resting_order.filled_quantity,
        )

    def _remove_order(self, side, order):
        book_side = self.order_book[side]
        book_side[order.price].remove(order)
        if not book_side[order.price]:
            del book_side[order.price]

    def _get_opposite(self, order):
        if order.side == "BUY":
            return self.best_asks(), "asks"
        return self.best_bids(), "bids"

    def match(self, order):
        while order.filled_quantity < order.quantity:
            best_order, book_side = self._get_opposite(order)
            if not best_order:
                break

            price_match = (
                order.type_order == "MKT"
                or (order.side == "BUY" and order.price >= best_order.price)
                or (order.side == "SELL" and order.price <= best_order.price)
            )

            if price_match:
                volume = self._trade_volume(order, best_order)
                order.filled_quantity += volume
                best_order.filled_quantity += volume

                trade_price = (
                    best_order.price if best_order.type_order == "LMT" else order.price
                )
                order.execution_price = trade_price
                best_order.execution_price = trade_price

                best_order.update_status()
                order.update_status()

                if best_order.status == "FILLED":
                    self._remove_order(book_side, best_order)

                self.order_book["last_price"] = trade_price
            else:
                break
        order.update_status()

    def __str__(self):
        result = "Order Book:\n"
        result += "Bids:\n"
        for price in sorted(self.order_book["bids"].keys(), reverse=True):
            for order in self.order_book["bids"][price]:
                result += f"  {repr(order)}\n"
        result += "Asks:\n"
        for price in sorted(self.order_book["asks"].keys()):
            for order in self.order_book["asks"][price]:
                result += f"  {repr(order)}\n"
        return result


class StockExchange:
    def __init__(self):
        self.exchange = {}
        self.orders = {}
        self.next_order_id = 1

    def place_order(self, side, stock_name, type_order, price, quantity):
        order = Order(self.next_order_id, side, stock_name, type_order, price, quantity)
        self.orders[self.next_order_id] = order
        if stock_name not in self.exchange:
            self.exchange[stock_name] = OrderBook()
        order_book = self.exchange[stock_name]

        order_book.match(order)
        if order.status != "FILLED":
            order_book.add_order(order)

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
            return False, "Quit format: QUIT"

        if parts[0] == "BOOK" and len(parts) != 2:
            return False, "Book format: BOOK <stock_name>"

        if parts[0] in ("BUY", "SELL"):
            if len(parts) < 4:
                return False, "Invalid command"

            type_order = parts[2]
            stock = parts[1]
            if not stock.isalpha() or not stock.isupper():
                return False, "Stock name must be alphabetic and uppercase"
            if type_order not in ("MKT", "LMT"):
                return False, "Invalid order type, must be MKT or LMT"

            if type_order == "MKT":
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

            if type_order == "LMT":
                if len(parts) != 5:
                    return (
                        False,
                        "Limit order format: BUY|SELL <stock_name> LMT $<price> <quantity>",
                    )
                try:
                    price = float(parts[3].replace("$", ""))
                    if price <= 0:
                        return False, "Price must be a positive number"
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
            stock_name = parts[1]
            type_order = parts[2]
            if type_order == "MKT":
                price = None
                quantity = int(parts[3])
            else:
                price = float(parts[3][1:]) if parts[3].startswith("$") else None
                quantity = int(parts[4])
            order = self.place_order(parts[0], stock_name, type_order, price, quantity)
            return order
        elif len(parts) >= 2 and parts[0] == "VIEW" and parts[1] == "ORDERS":
            print(self.get_orders())
        elif parts[0] == "QUOTE" and len(parts) > 1:
            stock_name = parts[1]
            print(self.quote(stock_name))
        elif parts[0] == "BOOK" and len(parts) > 1:
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
            best_bid = order_book.best_bids()
            best_ask = order_book.best_asks()
            last_price = order_book.order_book["last_price"]
            bid_str = f"BID: ${best_bid.price:.2f}" if best_bid else "BID: N/A"
            ask_str = f"ASK: ${best_ask.price:.2f}" if best_ask else "ASK: N/A"
            last_price_str = (
                f"LAST: ${last_price:.2f}" if last_price is not None else "LAST: N/A"
            )
            return f"{stock_name} {bid_str} {ask_str} {last_price_str}"
        else:
            return f"No data for {stock_name}"


def start_trading():
    stock_exchange = StockExchange()
    while True:
        command = input("Action: ")
        valid, error = stock_exchange.validate_command(command)
        parts = command.split()
        if not valid:
            print(error)
            continue
        if parts[0] == "QUIT":
            print("No output")
            break

        order = stock_exchange.process_command(command)
        if order:
            print(order)


if __name__ == "__main__":
    start_trading()
