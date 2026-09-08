from customers import Customer
from menu import Menu
from menu_item import MenuItem
from payment import CashPayment
from restaurant import Restaurant


def main() -> None:
    """Run a small end-to-end Restaurant POS example."""
    menu = Menu()
    restaurant = Restaurant("Good Food Restaurant", menu)

    fried_rice = MenuItem(1, "Fried Rice", 60.00)
    iced_tea = MenuItem(2, "Iced Tea", 25.00)
    restaurant.addMenuItem(fried_rice)
    restaurant.addMenuItem(iced_tea)

    customer = Customer(1, "Somchai", "081-234-5678")
    order = restaurant.createOrder(customer)
    order.addItem(fried_rice, 2)
    order.addItem(iced_tea, 1)

    total = order.calculateTotal()
    print(f"Order #{order.orderId} for {customer.name}")
    print(f"Total: ${total:.2f}")

    payment = CashPayment(total, 150.00)
    if payment.pay():
        order.checkout()
        order.complete()
        print(f"Order status: {order.orderStatus.value}")


if __name__ == "__main__":
    main()
