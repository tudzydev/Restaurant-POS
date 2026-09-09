"""Table management domain model."""

from enum import Enum
from typing import Optional


class TableStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class Table:
    def __init__(self, table_id: str, capacity: int = 4, section: str = "Indoor"):
        self.__table_id = table_id
        self.__capacity = capacity
        self.__section = section
        self.__status = TableStatus.AVAILABLE
        self.__current_order_id: Optional[int] = None

    @property
    def table_id(self) -> str:
        return self.__table_id

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def section(self) -> str:
        return self.__section

    @property
    def status(self) -> TableStatus:
        return self.__status

    @property
    def current_order_id(self) -> Optional[int]:
        return self.__current_order_id

    def occupy(self, order_id: int) -> None:
        if self.__status == TableStatus.OCCUPIED and self.__current_order_id != order_id:
            raise ValueError(f"Table {self.__table_id} is already occupied by order #{self.__current_order_id}")
        self.__status = TableStatus.OCCUPIED
        self.__current_order_id = order_id

    def release(self) -> None:
        self.__status = TableStatus.AVAILABLE
        self.__current_order_id = None

    def reserve(self) -> None:
        if self.__status == TableStatus.OCCUPIED:
            raise ValueError(f"Cannot reserve an occupied table {self.__table_id}")
        self.__status = TableStatus.RESERVED

    def to_dict(self) -> dict:
        return {
            "tableId": self.__table_id,
            "capacity": self.__capacity,
            "section": self.__section,
            "status": self.__status.value,
            "currentOrderId": self.__current_order_id,
        }
