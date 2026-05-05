from project.enums import Side


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

    def best_bid(self):
        if not self.bids:
            return None

        best_price = max(self.bids.keys())
        return self.bids[best_price][0]

    def best_ask(self):
        if not self.asks:
            return None

        best_price = min(self.asks.keys())
        return self.asks[best_price][0]

    def get_opposite(self, order):
        if order.side == Side.BUY:
            return self.best_ask(), Side.SELL
        return self.best_bid(), Side.BUY

    def remove_order(self, side, order):
        price_key = order.price if order.price is not None else None
        book = self._get_book(side)
        if price_key not in book:
            return
        if order not in book[price_key]:
            return
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
