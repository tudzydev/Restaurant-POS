import json
import unittest
from urllib.request import Request, urlopen
import threading
import time
from server import run, POSRequestHandler
import socketserver

PORT_TEST = 8089

class TestServerSpecification(unittest.TestCase):
    """Specification tests for server API endpoints."""

    @classmethod
    def setUpClass(cls):
        # Start server in background thread
        cls.httpd = socketserver.TCPServer(("", PORT_TEST), POSRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_get_menu_endpoint(self):
        """GET /api/menu returns JSON list of menu items."""
        url = f"http://localhost:{PORT_TEST}/api/menu"
        with urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            self.assertEqual(data[0]["id"], 1)

    def test_checkout_endpoint_successful_cash(self):
        """POST /api/orders/checkout with sufficient cash completes the order."""
        url = f"http://localhost:{PORT_TEST}/api/orders/checkout"
        payload = {
            "customerName": "Nong Somchai",
            "customerPhone": "081-999-8888",
            "items": [{"id": 1, "quantity": 2}], # 2x 60.00 = 120.00
            "payment": {"method": "cash", "receivedAmount": 150.00}
        }
        req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urlopen(req) as response:
            self.assertEqual(response.status, 200)
            res_data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(res_data["success"])
            self.assertEqual(res_data["status"], "completed")
            self.assertEqual(res_data["total"], 120.00)


if __name__ == "__main__":
    unittest.main()
