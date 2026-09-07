class Customer:
    def __init__(self, id: int, name: str, phone: str):
        self.__id = id
        self.__name = name
        self.__phone = phone

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone
    
    def getInfo(self) -> str:
        return f"customer:{self.__name} {self.__phone}"