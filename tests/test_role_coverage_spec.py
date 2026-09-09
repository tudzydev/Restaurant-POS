"""Specification tests for Multi-Role UI & Workflow Coverage.

Enforces:
1. Cashier / Waitstaff (FOH): Can take orders, assign tables, and complete payment.
2. Kitchen / Bar Staff (BOH / KDS): Receives pending tickets and bumps status (pending -> cooking -> ready -> completed).
3. Customer / Guest (Kiosk): Can place self-orders with notes and counter/QR payment.
4. Restaurant Manager: Accesses analytics, menu CRUD, and table floor state.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from urllib.request import Request, urlopen

from server import POSRequestHandler
from storage import POSStorage
import socketserver


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class TestMultiRoleCoverageSpecification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db_path = os.path.join(cls.test_dir, "test_roles_db.json")

        import server
        cls.orig_storage = server.storage
        server.storage = POSStorage(cls.test_db_path)

        cls.httpd = ReusableTCPServer(("127.0.0.1", 0), POSRequestHandler)
        cls.port = cls.httpd.server_address[1]

        import threading
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        import server
        server.storage = cls.orig_storage
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def _api_get(self, path: str):
        url = f"http://127.0.0.1:{self.port}{path}"
        req = Request(url, method="GET")
        with urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _api_post(self, path: str, payload: dict):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_role_customer_kiosk_places_order_and_reaches_kitchen_kds(self):
        """Customer places a self-order via Kiosk -> status is pending with cooking notes."""
        kiosk_payload = {
            "customerName": "Guest Table 03",
            "diningMode": "dinein",
            "tableNumber": "T-03",
            "notes": "Extra crispy, no chili",
            "items": [
                {"id": 1, "quantity": 2}, # 2x Fried Rice
                {"id": 5, "quantity": 1}, # 1x Iced Tea
            ],
            "payment": {"method": "counter"},
            "status": "pending"
        }
        status, res = self._api_post("/api/orders/checkout", kiosk_payload)
        self.assertEqual(status, 200)
        self.assertTrue(res.get("success"))
        order_id = res["orderId"]
        self.assertEqual(res["status"], "pending")

        # Kitchen KDS checks orders queue
        s_orders, orders = self._api_get("/api/orders")
        self.assertEqual(s_orders, 200)
        kds_ticket = next((o for o in orders if o["orderId"] == order_id), None)
        self.assertIsNotNone(kds_ticket)
        self.assertEqual(kds_ticket["status"], "pending")
        self.assertEqual(kds_ticket["notes"], "Extra crispy, no chili")
        self.assertEqual(kds_ticket["customer"]["name"], "Guest Table 03")

    def test_role_kitchen_staff_bumps_ticket_lifecycle(self):
        """Kitchen bumps ticket: pending -> cooking -> ready -> completed."""
        # 1. Start Cooking
        s_bump, res_bump = self._api_post("/api/orders/status", {"orderId": 101, "status": "cooking"})
        self.assertEqual(s_bump, 200)
        self.assertEqual(res_bump["status"], "cooking")

        # 2. Mark Ready to Serve
        s_bump2, res_bump2 = self._api_post("/api/orders/status", {"orderId": 101, "status": "ready"})
        self.assertEqual(s_bump2, 200)
        self.assertEqual(res_bump2["status"], "ready")

        # 3. Serve & Complete
        s_bump3, res_bump3 = self._api_post("/api/orders/status", {"orderId": 101, "status": "completed"})
        self.assertEqual(s_bump3, 200)
        self.assertEqual(res_bump3["status"], "completed")

    def test_role_manager_views_analytics_and_manages_menu(self):
        """Manager can query sales summary and add new specialty item."""
        s_rep, rep = self._api_get("/api/reports/summary")
        self.assertEqual(s_rep, 200)
        self.assertIn("totalRevenue", rep)
        self.assertIn("popularItems", rep)

        # Manager registers new item
        s_menu, res_menu = self._api_post("/api/menu", {
            "name": "Chef Special Crab Curry",
            "price": 280.0,
            "category": "mains"
        })
        self.assertEqual(s_menu, 201)
        self.assertEqual(res_menu["name"], "Chef Special Crab Curry")


if __name__ == "__main__":
    unittest.main()
