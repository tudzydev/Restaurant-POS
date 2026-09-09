class MenuItem:
    def __init__(self, id: int, name: str, price: float, category: str = "mains"):
        self.__id = id
        self.__name = name
        self.__price = price
        self.__category = category

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price

    @property
    def category(self) -> str:
        return self.__category
        
    def getPrice(self) -> float:
        return self.__price