#!/usr/bin/env python3
"""Restaurant POS Full-Stack Web Application Server.

Provides full REST APIs for Menu CRUD, Table management, Kitchen Order Tickets (KDS),
Customer Directory, Orders & Payments, and Sales Analytics, with persistent storage.
"""

from __future__ import annotations

from datetime import datetime
import http.server
import json
import os
import socketserver
import sys
from urllib.parse import parse_qs, urlparse

from customers import Customer
from menu import Menu
from menu_item import MenuItem
from payment import CashPayment, CreditCardPayment, QRPayment
from restaurant import Restaurant
from storage import POSStorage
from tables import Table, TableStatus

PORT = 8000
storage = POSStorage()

# Initialize In-Memory Domain Engine synchronized with Storage
db_data = storage.load_all()
pos_menu = Menu()
for m in db_data.get("menu", []):
    pos_menu.addItem(MenuItem(m["id"], m["name"], float(m["price"]), m.get("category", "mains")))

pos_restaurant = Restaurant("TableOne Restaurant", pos_menu)


class POSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler serving static files & Full REST API."""

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.end_headers()

    def send_json(self, status_code: int, data: dict | list) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 1. GET /api/menu
        if path == "/api/menu":
            data = storage.load_all()
            self.send_json(200, data.get("menu", []))
            return

        # 2. GET /api/tables
        if path == "/api/tables":
            data = storage.load_all()
            self.send_json(200, data.get("tables", []))
            return

        # 3. GET /api/customers
        if path == "/api/customers":
            data = storage.load_all()
            self.send_json(200, data.get("customers", []))
            return

        # 4. GET /api/orders
        if path == "/api/orders":
            data = storage.load_all()
            self.send_json(200, data.get("orders", []))
            return

        # 5. GET /api/reports/summary
        if path == "/api/reports/summary":
            summary = storage.get_summary_reports()
            self.send_json(200, summary)
            return

        # Fallback to static web files
        super().do_GET()

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        # 1. POST /api/menu (Add new menu item)
        if path == "/api/menu":
            name = body.get("name")
            price = float(body.get("price", 0))
            category = body.get("category", "mains")
            if not name or price <= 0:
                self.send_json(400, {"error": "Invalid name or price"})
                return

            db_data = storage.load_all()
            new_id = max([item["id"] for item in db_data.get("menu", [])] or [0]) + 1
            new_item = {"id": new_id, "name": name, "price": price, "category": category}
            db_data["menu"].append(new_item)
            storage.save_all(db_data)
            pos_restaurant.addMenuItem(MenuItem(new_id, name, price, category))
            self.send_json(201, new_item)
            return

        # 2. POST /api/orders/checkout (Process order & payment)
        if path == "/api/orders/checkout":
            try:
                customer_name = body.get("customerName", "Walk-in Guest")
                customer_phone = body.get("customerPhone", "")
                items = body.get("items", [])
                payment_info = body.get("payment", {})
                dining_mode = body.get("diningMode", "dinein")
                table_number = body.get("tableNumber", "T-01") if dining_mode == "dinein" else "Takeaway"

                if not items:
                    self.send_json(400, {"error": "Order cannot be empty"})
                    return

                # Create Order
                db_data = storage.load_all()
                next_id = db_data.get("next_order_id", 101)
                customer = Customer(len(db_data.get("customers", [])) + 1, customer_name, customer_phone)
                order = pos_restaurant.createOrder(customer)

                order_items_payload = []
                for itm in items:
                    item_id = itm["id"]
                    qty = int(itm.get("quantity", 1))
                    menu_item = pos_restaurant.menu.findItem(item_id)
                    if not menu_item:
                        # try load from storage
                        found = next((m for m in db_data.get("menu", []) if m["id"] == item_id), None)
                        if found:
                            menu_item = MenuItem(found["id"], found["name"], found["price"], found.get("category", "mains"))
                            pos_restaurant.addMenuItem(menu_item)
                        else:
                            raise ValueError(f"Menu item #{item_id} not found")

                    order.addItem(menu_item, qty)
                    order_items_payload.append({
                        "id": menu_item.id,
                        "name": menu_item.name,
                        "price": menu_item.price,
                        "quantity": qty,
                        "subtotal": menu_item.price * qty,
                    })

                subtotal = order.calculateTotal()
                tax = subtotal * 0.07
                grand_total = subtotal + tax

                # Process Payment
                method = payment_info.get("method", "cash").lower()
                payment_success = False

                if method == "cash":
                    received = float(payment_info.get("receivedAmount", grand_total))
                    payment = CashPayment(grand_total, received)
                    payment_success = payment.pay()
                elif method == "card":
                    card_num = payment_info.get("cardNumber", "")
                    payment = CreditCardPayment(grand_total, card_num)
                    payment_success = payment.pay()
                elif method == "qr":
                    txn_id = payment_info.get("transactionId", "")
                    payment = QRPayment(grand_total, txn_id)
                    payment_success = payment.pay()
                else:
                    raise ValueError(f"Unknown payment method: {method}")

                if not payment_success:
                    order.cancel()
                    self.send_json(400, {"error": "Payment failed", "status": order.orderStatus.value})
                    return

                order.checkout()
                order.complete()

                # Update table status if dine-in
                if dining_mode == "dinein":
                    for t in db_data.get("tables", []):
                        if t.get("tableId") == table_number:
                            t["status"] = "occupied"
                            t["currentOrderId"] = next_id

                order_record = {
                    "orderId": next_id,
                    "customer": {"name": customer_name, "phone": customer_phone},
                    "diningMode": dining_mode,
                    "tableNumber": table_number,
                    "items": order_items_payload,
                    "subtotal": round(subtotal, 2),
                    "tax": round(tax, 2),
                    "total": round(grand_total, 2),
                    "status": "completed",
                    "paymentMethod": method.capitalize(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                storage.add_order(order_record)
                self.send_json(200, {
                    "success": True,
                    "orderId": order_record["orderId"],
                    "status": order_record["status"],
                    "total": order_record["total"],
                    "order": order_record,
                })

            except Exception as exc:
                self.send_json(400, {"error": str(exc)})
            return

        # 3. POST /api/orders/status (Kitchen KDS status transition)
        if path == "/api/orders/status":
            order_id = int(body.get("orderId", 0))
            new_status = body.get("status", "completed")
            updated = storage.update_order_status(order_id, new_status)
            if updated:
                self.send_json(200, {"success": True, "orderId": order_id, "status": new_status})
            else:
                self.send_json(404, {"error": f"Order #{order_id} not found"})
            return

        # 4. POST /api/tables/status (Update table occupied/available)
        if path == "/api/tables/status":
            table_id = body.get("tableId")
            new_status = body.get("status", "available")
            db_data = storage.load_all()
            found = False
            for t in db_data.get("tables", []):
                if t.get("tableId") == table_id:
                    t["status"] = new_status
                    if new_status == "available":
                        t["currentOrderId"] = None
                    found = True
                    break
            if found:
                storage.save_all(db_data)
                self.send_json(200, {"success": True, "tableId": table_id, "status": new_status})
            else:
                self.send_json(404, {"error": f"Table {table_id} not found"})
            return

        # 5. POST /api/customers (Create customer profile)
        if path == "/api/customers":
            name = body.get("name", "").strip()
            phone = body.get("phone", "").strip()
            if not name:
                self.send_json(400, {"error": "Name is required"})
                return

            db_data = storage.load_all()
            new_id = len(db_data.get("customers", [])) + 1
            cust = {"id": new_id, "name": name, "phone": phone}
            db_data["customers"].append(cust)
            storage.save_all(db_data)
            self.send_json(201, cust)
            return

        self.send_json(404, {"error": "Endpoint not found"})

    def do_DELETE(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # DELETE /api/menu/:id
        if path.startswith("/api/menu/"):
            try:
                item_id = int(path.split("/")[-1])
                db_data = storage.load_all()
                orig_len = len(db_data.get("menu", []))
                db_data["menu"] = [m for m in db_data.get("menu", []) if m["id"] != item_id]
                if len(db_data["menu"]) < orig_len:
                    storage.save_all(db_data)
                    pos_restaurant.menu.removeItem(item_id)
                    self.send_json(200, {"success": True, "deletedId": item_id})
                else:
                    self.send_json(404, {"error": f"Menu item #{item_id} not found"})
            except Exception as exc:
                self.send_json(400, {"error": str(exc)})
            return

        self.send_json(404, {"error": "Endpoint not found"})


def run(port: int = PORT) -> None:
    handler = POSRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print("=" * 60)
        print("  🍽️  TableOne Restaurant POS - Full Engine Online")
        print(f"  --> Local Web Terminal: http://localhost:{port}")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port_arg)
