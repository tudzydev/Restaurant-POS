from enum import Enum
from customers import Customer
from order_item import OrderItem
from menu_item import MenuItem


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order:
    def __init__(
        self,
        orderId: int,
        customer: Customer,
        orderStatus: OrderStatus
    ):
        self.__orderId = orderId
        self.__customer = customer
        self.__items: list[OrderItem] = []
        self.__orderStatus = orderStatus

    @property
    def orderId(self) -> int:
        return self.__orderId

    @property
    def customer(self) -> Customer:
        return self.__customer

    @property
    def items(self) -> list[OrderItem]:
        return self.__items

    @property
    def orderStatus(self) -> OrderStatus:
        return self.__orderStatus

    def addItem(self, menuItem: MenuItem, quantity: int) -> None:
        if self.__orderStatus != OrderStatus.PENDING:
            raise ValueError("Cannot add items to an order that is not pending")
        item = OrderItem(menuItem, quantity)
        self.__items.append(item)

    def removeItem(self, itemId: int) -> None:
        if self.__orderStatus != OrderStatus.PENDING:
            raise ValueError("Cannot remove items from an order that is not pending")
        self.__items = [
            item for item in self.__items
            if item.menu_item.id != itemId
        ]

    def calculateTotal(self) -> float:
        return sum(
            item.calculate_subtotal()
            for item in self.__items
        )

    def checkout(self) -> None:
        if not self.__items:
            raise ValueError("Order is empty")

        if self.__orderStatus != OrderStatus.PENDING:
            raise ValueError("Order cannot be checked out")

        self.__orderStatus = OrderStatus.CONFIRMED

    def complete(self) -> None:
        if self.__orderStatus != OrderStatus.CONFIRMED:
            raise ValueError("Order must be confirmed first")

        self.__orderStatus = OrderStatus.COMPLETED

    def cancel(self) -> None:
        if self.__orderStatus == OrderStatus.COMPLETED:
            raise ValueError("Completed order cannot be cancelled")

        self.__orderStatus = OrderStatus.CANCELLED
