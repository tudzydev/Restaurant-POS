import unittest
from customers import Customer
from menu_item import MenuItem
from order_item import OrderItem
from orders import Order, OrderStatus


class TestOrderSpecification(unittest.TestCase):
    """Executable specifications for Order & OrderItem (Section 6, Features 2 & 3 and Section 3)."""

    def setUp(self):
        self.customer = Customer(1, "Somchai", "081-234-5678")
        self.item_rice = MenuItem(1, "Fried Rice", 60.00)
        self.item_tea = MenuItem(2, "Iced Tea", 25.00)
        self.order = Order(1, self.customer, OrderStatus.PENDING)

    # --- Feature 2: Order Computation ---

    def test_scenario_2_1_subtotal_calculation(self):
        """Scenario 2.1: Subtotal calculation for OrderItem."""
        # Given a MenuItem with price 60.00 and quantity 2
        order_item = OrderItem(self.item_rice, 2)

        # When calculate_subtotal() is called
        subtotal = order_item.calculate_subtotal()

        # Then subtotal is 120.00
        self.assertEqual(subtotal, 120.00)

    def test_scenario_2_2_order_total_calculation(self):
        """Scenario 2.2: Order total calculation."""
        # Given an Order with 2 Fried Rice (60.00 ea) and 1 Iced Tea (25.00 ea)
        self.order.addItem(self.item_rice, 2)
        self.order.addItem(self.item_tea, 1)

        # When order.calculateTotal() is executed
        total = self.order.calculateTotal()

        # Then total is 145.00
        self.assertEqual(total, 145.00)

    def test_remove_item_from_order(self):
        """Order item removal removes all items matching menuItem id."""
        self.order.addItem(self.item_rice, 2)
        self.order.addItem(self.item_tea, 1)
        self.order.removeItem(self.item_rice.id)

        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].menu_item.id, self.item_tea.id)
        self.assertEqual(self.order.calculateTotal(), 25.00)

    def test_invalid_quantity_raises_error(self):
        """Invariant: OrderItem quantity must be > 0."""
        with self.assertRaises(ValueError) as ctx:
            self.order.addItem(self.item_rice, 0)
        self.assertIn("Quantity must be greater than 0", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.order.addItem(self.item_rice, -3)
        self.assertIn("Quantity must be greater than 0", str(ctx.exception))

    def test_add_item_to_non_pending_order_raises_error(self):
        """Invariant: Cannot add items to a confirmed or completed order."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        with self.assertRaises(ValueError) as ctx:
            self.order.addItem(self.item_tea, 1)
        self.assertIn("Cannot add items to an order that is not pending", str(ctx.exception))

    def test_remove_item_from_non_pending_order_raises_error(self):
        """Invariant: Cannot remove items from a confirmed or completed order."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        with self.assertRaises(ValueError) as ctx:
            self.order.removeItem(self.item_rice.id)
        self.assertIn("Cannot remove items from an order that is not pending", str(ctx.exception))

    # --- Feature 3 & Section 3: State Transition Invariants ---

    def test_scenario_3_1_empty_order_checkout_rejection(self):
        """Scenario 3.1: Empty order checkout rejection."""
        # Given an order with 0 items
        self.assertEqual(len(self.order.items), 0)

        # When checkout() is called, Then ValueError("Order is empty") is raised
        with self.assertRaises(ValueError) as ctx:
            self.order.checkout()
        self.assertIn("Order is empty", str(ctx.exception))

    def test_valid_checkout_transitions_to_confirmed(self):
        """Transition: PENDING -> CONFIRMED."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        self.assertEqual(self.order.orderStatus, OrderStatus.CONFIRMED)

    def test_checkout_when_not_pending_raises_error(self):
        """Precondition: Cannot checkout if already confirmed."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()

        with self.assertRaises(ValueError) as ctx:
            self.order.checkout()
        self.assertIn("Order cannot be checked out", str(ctx.exception))

    def test_scenario_3_2_direct_completion_rejection(self):
        """Scenario 3.2: Direct completion rejection from PENDING."""
        # Given an order in PENDING status
        self.assertEqual(self.order.orderStatus, OrderStatus.PENDING)

        # When complete() is called, Then ValueError is raised
        with self.assertRaises(ValueError) as ctx:
            self.order.complete()
        self.assertIn("Order must be confirmed first", str(ctx.exception))

    def test_valid_complete_transitions_from_confirmed(self):
        """Transition: CONFIRMED -> COMPLETED."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        self.order.complete()
        self.assertEqual(self.order.orderStatus, OrderStatus.COMPLETED)

    def test_scenario_3_3_completed_order_cancellation_rejection(self):
        """Scenario 3.3: Completed order cancellation rejection."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        self.order.complete()

        # Given an order in COMPLETED status, cancel() raises ValueError
        with self.assertRaises(ValueError) as ctx:
            self.order.cancel()
        self.assertIn("Completed order cannot be cancelled", str(ctx.exception))

    def test_cancel_pending_order_succeeds(self):
        """Transition: PENDING -> CANCELLED."""
        self.order.cancel()
        self.assertEqual(self.order.orderStatus, OrderStatus.CANCELLED)

    def test_cancel_confirmed_order_succeeds(self):
        """Transition: CONFIRMED -> CANCELLED."""
        self.order.addItem(self.item_rice, 1)
        self.order.checkout()
        self.order.cancel()
        self.assertEqual(self.order.orderStatus, OrderStatus.CANCELLED)


if __name__ == "__main__":
    unittest.main()
