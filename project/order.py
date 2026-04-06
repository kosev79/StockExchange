import time
from dataclasses import dataclass, field


@dataclass
class Order:
    id: int
    side: str
    stock_name: str
    type_order: str
    price: float | None = None
    quantity: int = 0
    execution_price: float | None = None
    filled_quantity: int = 0
    status: str = "PENDING"
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        self.side = self.side.upper()
        self.type_order = self.type_order.upper()
        # if self.price is None:
        #     self.price = float("inf") if self.side == "BUY" else 0.0
        if self.type_order == "MKT":
            self.price = None

    def update_status(self):
        if self.filled_quantity == 0:
            self.status = "PENDING"
        elif 0 < self.filled_quantity < self.quantity:
            self.status = "PARTIAL"
        else:
            self.status = "FILLED"

    def __str__(self):
        side = "покупку" if self.side == "BUY" else "продажу"
        if self.type_order == "LMT":
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
