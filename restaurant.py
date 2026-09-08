from menu import Menu
from orders import Order, OrderStatus
from menu_item import MenuItem
from customers import Customer


class Restaurant:
    def __init__(self, name: str, menu: Menu):
        self.__name = name
        self.__menu = menu
        self.__orders: list[Order] = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def menu(self) -> Menu:
        return self.__menu

    @property
    def orders(self) -> list[Order]:
        return self.__orders

    def addMenuItem(self, item: MenuItem) -> None:
        self.__menu.addItem(item)

    def createOrder(self, customer: Customer) -> Order:
        order = Order(
            len(self.__orders) + 1,
            customer,
            OrderStatus.PENDING
        )

        self.__orders.append(order)

        return order