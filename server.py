#!/usr/bin/env python3
"""Restaurant POS Web Application Server.

Serves the POS frontend static assets and provides REST API endpoints
connected directly to the Python domain model.
"""

import http.server
import json
import socketserver
import sys
from urllib.parse import urlparse

from customers import Customer
from menu import Menu
from menu_item import MenuItem
from payment import CashPayment, CreditCardPayment, QRPayment
from restaurant import Restaurant

PORT = 8000

# Initialize Domain Engine
pos_menu = Menu()
pos_restaurant = Restaurant("TableOne Restaurant", pos_menu)

# Seed standard menu items
pos_restaurant.addMenuItem(MenuItem(1, "Fried Rice (ข้าวผัด)", 60.00, "mains"))
pos_restaurant.addMenuItem(MenuItem(2, "Pad Thai (ผัดไทย)", 80.00, "mains"))
pos_restaurant.addMenuItem(MenuItem(3, "Green Curry (แกงเขียวหวาน)", 120.00, "mains"))
pos_restaurant.addMenuItem(MenuItem(4, "Tom Yum Kung (ต้มยำกุ้ง)", 150.00, "mains"))
pos_restaurant.addMenuItem(MenuItem(5, "Iced Tea (ชาเย็น)", 25.00, "drinks"))
pos_restaurant.addMenuItem(MenuItem(6, "Thai Milk Tea (ชาไทย)", 35.00, "drinks"))
pos_restaurant.addMenuItem(MenuItem(7, "Fresh Coconut (น้ำมะพร้าว)", 45.00, "drinks"))
pos_restaurant.addMenuItem(MenuItem(8, "Mango Sticky Rice (ข้าวเหนียวมะม่วง)", 90.00, "desserts"))
pos_restaurant.addMenuItem(MenuItem(9, "Coconut Ice Cream (ไอติมกะทิ)", 50.00, "desserts"))


class POSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler serving static files & REST endpoints."""

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/menu":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            menu_data = [
                {
                    "id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "category": getattr(item, "category", "mains"),
                }
                for item in pos_restaurant.menu.items
            ]
            self.wfile.write(json.dumps(menu_data).encode("utf-8"))
            return

        if parsed_url.path == "/api/orders":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            orders_data = [
                {
                    "orderId": o.orderId,
                    "customer": o.customer.name,
                    "status": o.orderStatus.value,
                    "total": o.calculateTotal(),
                    "items": [
                        {
                            "id": item.menu_item.id,
                            "name": item.menu_item.name,
                            "price": item.menu_item.price,
                            "quantity": item.quantity,
                            "subtotal": item.calculate_subtotal(),
                        }
                        for item in o.items
                    ],
                }
                for o in pos_restaurant.orders
            ]
            self.wfile.write(json.dumps(orders_data).encode("utf-8"))
            return

        # Default fallback to static files (index.html, styles.css, app.js, etc.)
        super().do_GET()

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/orders/checkout":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                customer_name = data.get("customerName", "Walk-in Guest")
                customer_phone = data.get("customerPhone", "")
                items = data.get("items", [])
                payment_info = data.get("payment", {})

                # 1. Create Customer and Order
                customer = Customer(len(pos_restaurant.orders) + 1, customer_name, customer_phone)
                order = pos_restaurant.createOrder(customer)

                # 2. Add Items
                for itm in items:
                    item_id = itm["id"]
                    qty = int(itm["quantity"])
                    menu_item = pos_restaurant.menu.findItem(item_id)
                    if not menu_item:
                        raise ValueError(f"Menu item #{item_id} not found")
                    order.addItem(menu_item, qty)

                # 3. Calculate Total
                total = order.calculateTotal()

                # 4. Process Payment
                method = payment_info.get("method", "cash").lower()
                payment_success = False

                if method == "cash":
                    received = float(payment_info.get("receivedAmount", total))
                    payment = CashPayment(total, received)
                    payment_success = payment.pay()
                elif method == "card":
                    card_num = payment_info.get("cardNumber", "")
                    payment = CreditCardPayment(total, card_num)
                    payment_success = payment.pay()
                elif method == "qr":
                    txn_id = payment_info.get("transactionId", "")
                    payment = QRPayment(total, txn_id)
                    payment_success = payment.pay()
                else:
                    raise ValueError(f"Unknown payment method: {method}")

                if not payment_success:
                    order.cancel()
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": "Payment failed", "orderStatus": order.orderStatus.value}).encode("utf-8")
                    )
                    return

                # 5. Transition Order: Checkout -> Complete
                order.checkout()
                order.complete()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response_payload = {
                    "success": True,
                    "orderId": order.orderId,
                    "customer": customer.name,
                    "status": order.orderStatus.value,
                    "total": total,
                }
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))

            except Exception as exc:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run(port: int = PORT) -> None:
    handler = POSRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"=====================================================")
        print(f"  Restaurant POS Web App running at:")
        print(f"  --> http://localhost:{port}")
        print(f"=====================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port_arg)
