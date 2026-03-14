from order import Order
from order_book import OrderBook


class MatchEngine:
    def _price_match(self, order, best_order):
        return (
            order.type_order == "MKT"
            or (order.side == "BUY" and order.price >= best_order.price)
            or (order.side == "SELL" and order.price <= best_order.price)
        )

    def _trade_volume(self, incoming_order, resting_order):
        return min(
            incoming_order.quantity - incoming_order.filled_quantity,
            resting_order.quantity - resting_order.filled_quantity,
        )

    def match(self, order_book: OrderBook, order: Order):
        while order.filled_quantity < order.quantity:
            best_order, book_side = order_book._get_opposite(order)

            if not best_order or not self._price_match(order, best_order):
                break

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
                order_book._remove_order(book_side, best_order)

            order_book.last_price = trade_price
        order.update_status()
