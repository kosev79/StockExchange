from src.project.order import Order
from src.project.order_book import OrderBook
from src.project.enums import Side, OrderType, OrderStatus


class MatchEngine:
    def _price_match(self, order, best_order):
        if order.type_order == OrderType.MKT or best_order.type_order == OrderType.MKT:
            return True
        if order.side == Side.BUY and best_order.price is not None:
            return order.price >= best_order.price
        if order.side == Side.SELL and best_order.price is not None:
            return order.price <= best_order.price
        return False

    def _trade_volume(self, incoming_order, resting_order):
        return min(
            incoming_order.quantity - incoming_order.filled_quantity,
            resting_order.quantity - resting_order.filled_quantity,
        )

    def _get_trade_price(self, best_order, order):
        if order.type_order == OrderType.MKT:
            return best_order.price
        if best_order.type_order == OrderType.MKT:
            return order.price
        return best_order.price if order.side == Side.BUY else order.price

    def match(self, order_book: OrderBook, order: Order):
        while order.filled_quantity < order.quantity:
            best_order, book_side = order_book.get_opposite(order)

            if not best_order or not self._price_match(order, best_order):
                break

            if (
                order.type_order == OrderType.MKT
                and best_order.type_order == OrderType.MKT
            ):
                break

            volume = self._trade_volume(order, best_order)
            if volume == 0:
                break

            order.filled_quantity += volume
            best_order.filled_quantity += volume

            trade_price = self._get_trade_price(best_order, order)

            order.execution_price = trade_price
            best_order.execution_price = trade_price

            best_order.update_status()
            order.update_status()

            if best_order.status == OrderStatus.FILLED:
                order_book.remove_order(book_side, best_order)

            order_book.last_price = trade_price
        order.update_status()
