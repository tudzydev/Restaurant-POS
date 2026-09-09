from menu_item import MenuItem


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        self.__menu_item = menu_item
        self.__quantity = quantity

    @property
    def menu_item(self) -> MenuItem:
        return self.__menu_item

    @property
    def quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__menu_item.price * self.__quantity