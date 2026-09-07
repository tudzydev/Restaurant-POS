from typing import Optional
from menu_item import MenuItem

class Menu:
    def __init__(self):
        self.__items: list[MenuItem] = []

    @property
    def items(self) -> list[MenuItem]:
        return self.__items

    def addItem(self, menuItem: MenuItem) -> None:
        self.__items.append(menuItem)

    def removeItem(self, itemId: int) -> bool:
        item = self.findItem(itemId)
        if item is not None:
            self.__items.remove(item)
            return True
        return False

    def findItem(self, itemId: int) -> Optional[MenuItem]:
        for item in self.__items:
            if item.id == itemId:
                return item
        return None