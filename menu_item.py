class MenuItem:
    def __init__(self, id: int, name: str, price: float):
        self.__id = id
        self.__name = name
        self.__price = price

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price
        
    def getPrice(self) -> float:
        return self.__price