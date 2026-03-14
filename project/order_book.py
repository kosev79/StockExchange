class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}
        self.last_price = None

    def _get_book(self, side):
        return self.bids if side == "BUY" else self.asks

    def add_order(self, order):
        book = self._get_book(order.side)
        if order.price not in book:
            book[order.price] = []
        book[order.price].append(order)

    def best_bids(self):
        if not self.bids:
            return None
        best_price = max(self.bids)
        return self.bids[best_price][0]

    def best_asks(self):
        if not self.asks:
            return None
        best_price = min(self.asks)
        return self.asks[best_price][0]

    def _get_opposite(self, order):
        if order.side == "BUY":
            return self.best_asks(), "SELL"
        return self.best_bids(), "BUY"

    def _remove_order(self, side, order):
        book = self._get_book(side)
        book[order.price].remove(order)
        if not book[order.price]:
            del book[order.price]

    def __str__(self):
        result = "Order Book:\n"
        result += "Bids:\n"
        for price in sorted(self.bids.keys(), reverse=True):
            for order in self.bids[price]:
                result += f"  {repr(order)}\n"
        result += "Asks:\n"
        for price in sorted(self.asks.keys()):
            for order in self.asks[price]:
                result += f"  {repr(order)}\n"
        return result
