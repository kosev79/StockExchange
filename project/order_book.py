from enums import Side


class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}
        self.last_price = None

    def _get_book(self, side):
        return self.bids if side == Side.BUY else self.asks

    def add_order(self, order):
        price_key = order.price if order.price is not None else None
        book = self._get_book(order.side)
        if price_key not in book:
            book[price_key] = []
        book[price_key].append(order)

    def best_bids(self):
        active_orders = [
            o
            for price in self.bids
            if price is not None
            for o in self.bids[price]
            if o.quantity - o.filled_quantity > 0
        ]
        if active_orders:
            best_order = max(active_orders, key=lambda o: o.price)
            self.last_best_bid = best_order
            return best_order
        return getattr(self, "last_best_bid", None)

    def best_asks(self):
        active_orders = [
            o
            for price in self.asks
            if price is not None
            for o in self.asks[price]
            if o.quantity - o.filled_quantity > 0
        ]
        if active_orders:
            best_order = min(active_orders, key=lambda o: o.price)
            self.last_best_ask = best_order
            return best_order
        return getattr(self, "last_best_ask", None)

    def get_opposite(self, order):
        if order.side == Side.BUY:
            return self.best_asks(), "SELL"
        return self.best_bids(), "BUY"

    def remove_order(self, side, order):
        price_key = order.price if order.price is not None else None
        book = self._get_book(side)
        book[price_key].remove(order)
        if not book[price_key]:
            del book[price_key]

    def __str__(self):
        result = "Order Book:\n"
        result += "Bids:\n"
        for price in sorted([p for p in self.bids if p is not None], reverse=True):
            for order in self.bids[price]:
                result += f"  {repr(order)}\n"
        result += "Asks:\n"
        for price in sorted([p for p in self.asks if p is not None]):
            for order in self.asks[price]:
                result += f"  {repr(order)}\n"
        return result
