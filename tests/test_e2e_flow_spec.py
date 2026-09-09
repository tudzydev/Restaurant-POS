import unittest
from customers import Customer
from menu import Menu
from menu_item import MenuItem
from orders import OrderStatus
from payment import CashPayment, CreditCardPayment, QRPayment
from restaurant import Restaurant


class TestEndToEndFlowSpecification(unittest.TestCase):
    """Executable specification for Section 5: End-to-End Sequence Flow."""

    def setUp(self):
        self.menu = Menu()
        self.restaurant = Restaurant("Good Food Restaurant", self.menu)

        # Setup menu items
        self.fried_rice = MenuItem(1, "Fried Rice", 60.00)
        self.iced_tea = MenuItem(2, "Iced Tea", 25.00)
        self.restaurant.addMenuItem(self.fried_rice)
        self.restaurant.addMenuItem(self.iced_tea)

        self.customer = Customer(1, "Somchai", "081-234-5678")

    def test_end_to_end_successful_cash_flow(self):
        """Sequence Flow: Create Order -> Add Items -> Calculate Total -> Cash Payment -> Checkout -> Complete."""
        # 1. Create order
        order = self.restaurant.createOrder(self.customer)
        self.assertEqual(order.orderId, 1)
        self.assertEqual(order.orderStatus, OrderStatus.PENDING)

        # 2. Add items
        order.addItem(self.fried_rice, 2)
        order.addItem(self.iced_tea, 1)

        # 3. Calculate total
        total = order.calculateTotal()
        self.assertEqual(total, 145.00)

        # 4. Process Payment
        payment = CashPayment(amount=total, receivedAmount=150.00)
        payment_success = payment.pay()
        self.assertTrue(payment_success)

        # 5. Checkout & Complete
        order.checkout()
        self.assertEqual(order.orderStatus, OrderStatus.CONFIRMED)

        order.complete()
        self.assertEqual(order.orderStatus, OrderStatus.COMPLETED)

    def test_end_to_end_failed_payment_leads_to_cancellation(self):
        """Sequence Flow: Create Order -> Add Items -> Failed Payment -> Cancel Order."""
        order = self.restaurant.createOrder(self.customer)
        order.addItem(self.fried_rice, 1)
        total = order.calculateTotal()

        # Insufficient funds
        payment = CashPayment(amount=total, receivedAmount=20.00)
        payment_success = payment.pay()
        self.assertFalse(payment_success)

        # Order is cancelled
        order.cancel()
        self.assertEqual(order.orderStatus, OrderStatus.CANCELLED)

    def test_multiple_orders_auto_increment_id(self):
        """Restaurant manages multiple orders with sequential IDs."""
        order1 = self.restaurant.createOrder(self.customer)
        order2 = self.restaurant.createOrder(self.customer)

        self.assertEqual(order1.orderId, 1)
        self.assertEqual(order2.orderId, 2)
        self.assertEqual(len(self.restaurant.orders), 2)


if __name__ == "__main__":
    unittest.main()
