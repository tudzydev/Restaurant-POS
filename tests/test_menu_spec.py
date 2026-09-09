import unittest
from menu import Menu
from menu_item import MenuItem


class TestMenuSpecification(unittest.TestCase):
    """Executable specifications for Menu & MenuItem (Section 6, Feature 1)."""

    def setUp(self):
        self.menu = Menu()
        self.item1 = MenuItem(1, "Fried Rice", 60.00)
        self.item2 = MenuItem(2, "Iced Tea", 25.00)

    def test_scenario_1_1_add_item_to_menu(self):
        """Scenario 1.1: Adding item to menu."""
        # Given an empty Menu
        self.assertEqual(len(self.menu.items), 0)

        # When addItem is called
        self.menu.addItem(self.item1)

        # Then findItem returns the item and items count equals 1
        self.assertEqual(len(self.menu.items), 1)
        found = self.menu.findItem(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Fried Rice")
        self.assertEqual(found.price, 60.00)

    def test_scenario_1_2_remove_existing_item(self):
        """Scenario 1.2: Removing existing item."""
        # Given a Menu with item ID 1
        self.menu.addItem(self.item1)

        # When removeItem(1) is called
        removed = self.menu.removeItem(1)

        # Then method returns True and findItem(1) returns None
        self.assertTrue(removed)
        self.assertIsNone(self.menu.findItem(1))
        self.assertEqual(len(self.menu.items), 0)

    def test_remove_nonexistent_item_returns_false(self):
        """Edge Case: Removing an item that does not exist in Menu returns False."""
        self.menu.addItem(self.item1)
        result = self.menu.removeItem(999)
        self.assertFalse(result)
        self.assertEqual(len(self.menu.items), 1)

    def test_menu_item_properties(self):
        """Contract: MenuItem exposes id, name, price and getPrice()."""
        self.assertEqual(self.item1.id, 1)
        self.assertEqual(self.item1.name, "Fried Rice")
        self.assertEqual(self.item1.price, 60.00)
        self.assertEqual(self.item1.getPrice(), 60.00)


if __name__ == "__main__":
    unittest.main()
