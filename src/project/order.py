import time
from dataclasses import dataclass, field
from src.project.enums import Side, OrderType, OrderStatus


@dataclass
class Order:
    id: int
    side: Side
    stock_name: str
    type_order: OrderType
    price: float | None = None
    quantity: int = 0
    execution_price: float | None = None
    filled_quantity: int = 0
    status: OrderStatus = OrderStatus.PENDING
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if self.type_order == OrderType.MKT:
            self.price = None

        if self.quantity <= 0:
            raise ValueError("Quantity must be greater then 0")

        if self.filled_quantity < 0:
            raise ValueError("Filled quantity cannot be negative")

        if self.filled_quantity > self.quantity:
            raise ValueError("Filled quantity cannot exeed total quantity")

    def update_status(self):
        if self.filled_quantity == 0:
            self.status = OrderStatus.PENDING
        elif 0 < self.filled_quantity < self.quantity:
            self.status = OrderStatus.PARTIAL
        else:
            self.status = OrderStatus.FILLED

    def __str__(self):
        side = "покупку" if self.side == Side.BUY else "продажу"
        if self.type_order == OrderType.LMT:
            return (
                f"Вы разместили лимитный ордер на {side} "
                f"{self.quantity} акций {self.stock_name} "
                f"по цене ${self.price:.2f} за акцию."
            )
        else:
            return (
                f"Вы разместили рыночный ордер на {side} "
                f"{self.quantity} акций {self.stock_name}"
            )

    def __repr__(self):
        if self.type_order == OrderType.LMT:
            price_str = f" ${self.price:.2f}"
        elif self.execution_price is not None:
            price_str = f" ${self.execution_price:.2f}"
        else:
            price_str = ""
        return (
            f"{self.id}. {self.stock_name} {self.type_order.value} {self.side.value}"
            f"{price_str} {self.filled_quantity}/{self.quantity} {self.status.value}"
        )
