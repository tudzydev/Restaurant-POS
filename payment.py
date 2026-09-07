from abc import ABC, abstractmethod


class Payment(ABC):
    def __init__(self, amount: float):
        self._amount = amount

    @property
    def amount(self) -> float:
        return self._amount

    @abstractmethod
    def pay(self) -> bool:
        pass


class CashPayment(Payment):
    def __init__(self, amount: float, receivedAmount: float):
        super().__init__(amount)
        self.__receivedAmount = receivedAmount

    @property
    def receivedAmount(self) -> float:
        return self.__receivedAmount

    def pay(self) -> bool:
        if self.__receivedAmount >= self._amount:
            change = self.__receivedAmount - self._amount
            print(f"Cash payment of ${self._amount:.2f} successful. Change: ${change:.2f}")
            return True
        print(f"Cash payment failed: Insufficient funds (Received: ${self.__receivedAmount:.2f}, Needed: ${self._amount:.2f})")
        return False


class CreditCardPayment(Payment):
    def __init__(self, amount: float, cardNumber: str):
        super().__init__(amount)
        self.__cardNumber = cardNumber

    @property
    def cardNumber(self) -> str:
        return self.__cardNumber

    def pay(self) -> bool:
        clean_number = self.__cardNumber.replace(" ", "").replace("-", "")
        if len(clean_number) == 16 and clean_number.isdigit():
            masked = f"****-****-****-{clean_number[-4:]}"
            print(f"Credit card payment of ${self._amount:.2f} successful using card {masked}.")
            return True
        print("Credit card payment failed: Invalid card number.")
        return False


class QRPayment(Payment):
    def __init__(self, amount: float, transactionId: str):
        super().__init__(amount)
        self.__transactionId = transactionId

    @property
    def transactionId(self) -> str:
        return self.__transactionId

    def pay(self) -> bool:
        if bool(self.__transactionId and self.__transactionId.strip()):
            print(f"QR code payment of ${self._amount:.2f} successful. Transaction ID: {self.__transactionId}")
            return True
        print("QR code payment failed: Missing transaction ID.")
        return False
    