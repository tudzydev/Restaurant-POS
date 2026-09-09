import json
import os
import shutil
import socketserver
import threading
import time
import unittest
from urllib.request import Request, urlopen

from server import POSRequestHandler
from storage import POSStorage
from tables import Table, TableStatus

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


TEST_DB = "data/test_database.json"


class TestFullSystemSpecification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean test DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

        cls.httpd = ReusableTCPServer(("", 0), POSRequestHandler)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    # --- Domain Model: Table Specifications ---

    def test_table_initial_state_available(self):
        """Table starts in AVAILABLE status."""
        table = Table("T-01", capacity=4, section="Indoor")
        self.assertEqual(table.status, TableStatus.AVAILABLE)
        self.assertIsNone(table.current_order_id)

    def test_table_occupy_and_release(self):
        """Table transitions from AVAILABLE -> OCCUPIED -> AVAILABLE."""
        table = Table("T-02", capacity=2)
        table.occupy(order_id=101)
        self.assertEqual(table.status, TableStatus.OCCUPIED)
        self.assertEqual(table.current_order_id, 101)

        # Re-occupying with another order raises ValueError
        with self.assertRaises(ValueError):
            table.occupy(order_id=102)

        table.release()
        self.assertEqual(table.status, TableStatus.AVAILABLE)
        self.assertIsNone(table.current_order_id)

    def test_table_reserve(self):
        """Table can be reserved if available."""
        table = Table("T-03", capacity=6)
        table.reserve()
        self.assertEqual(table.status, TableStatus.RESERVED)

    # --- Storage Persistence Specifications ---

    def test_storage_add_order_and_reports(self):
        """POSStorage saves orders and computes summary metrics correctly."""
        temp_storage = POSStorage(filepath=TEST_DB)
        order_payload = {
            "orderId": 999,
            "customer": {"name": "Test Customer", "phone": "000"},
            "diningMode": "dinein",
            "tableNumber": "T-01",
            "items": [
                {"id": 1, "name": "Fried Rice (ข้าวผัด)", "price": 60.0, "quantity": 2, "subtotal": 120.0}
            ],
            "subtotal": 120.0,
            "tax": 8.4,
            "total": 128.4,
            "status": "completed",
            "paymentMethod": "Cash",
            "timestamp": "2026-09-09 12:00:00",
        }
        temp_storage.add_order(order_payload)

        reports = temp_storage.get_summary_reports()
        self.assertGreaterEqual(reports["completedOrders"], 1)
        self.assertGreaterEqual(reports["totalRevenue"], 128.4)
        self.assertTrue(any(item["name"] == "Fried Rice (ข้าวผัด)" for item in reports["popularItems"]))

    # --- Full System REST APIs ---

    def test_api_tables_endpoint(self):
        """GET /api/tables returns list of restaurant tables."""
        url = f"http://localhost:{self.port}/api/tables"
        with urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            self.assertIn("tableId", data[0])

    def test_api_reports_summary_endpoint(self):
        """GET /api/reports/summary returns analytics."""
        url = f"http://localhost:{self.port}/api/reports/summary"
        with urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertIn("totalOrders", data)
            self.assertIn("totalRevenue", data)
            self.assertIn("popularItems", data)

    def test_api_menu_crud(self):
        """POST /api/menu and DELETE /api/menu/:id handles catalog lifecycle."""
        url = f"http://localhost:{self.port}/api/menu"
        new_item = {"name": "Spicy Basil Pork", "price": 75.0, "category": "mains"}
        req = Request(url, data=json.dumps(new_item).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urlopen(req) as response:
            self.assertEqual(response.status, 201)
            created = json.loads(response.read().decode("utf-8"))
            self.assertEqual(created["name"], "Spicy Basil Pork")
            created_id = created["id"]

        # Delete item
        del_url = f"http://localhost:{self.port}/api/menu/{created_id}"
        del_req = Request(del_url, method="DELETE")
        with urlopen(del_req) as del_res:
            self.assertEqual(del_res.status, 200)
            del_data = json.loads(del_res.read().decode("utf-8"))
            self.assertTrue(del_data["success"])


if __name__ == "__main__":
    unittest.main()
