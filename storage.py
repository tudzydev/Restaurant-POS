"""Persistence layer for Restaurant POS.

Saves and loads system state to/from a persistent JSON database file.
"""

import json
import os
from typing import Any, Dict, List


class POSStorage:
    def __init__(self, filepath: str = "data/pos_database.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        if not os.path.exists(self.filepath):
            self._init_default_db()

    def _init_default_db(self) -> None:
        default_data: Dict[str, Any] = {
            "menu": [
                {"id": 1, "name": "Fried Rice (ข้าวผัด)", "price": 60.0, "category": "mains"},
                {"id": 2, "name": "Pad Thai (ผัดไทย)", "price": 80.0, "category": "mains"},
                {"id": 3, "name": "Green Curry (แกงเขียวหวาน)", "price": 120.0, "category": "mains"},
                {"id": 4, "name": "Tom Yum Kung (ต้มยำกุ้ง)", "price": 150.0, "category": "mains"},
                {"id": 5, "name": "Iced Tea (ชาเย็น)", "price": 25.0, "category": "drinks"},
                {"id": 6, "name": "Thai Milk Tea (ชาไทย)", "price": 35.0, "category": "drinks"},
                {"id": 7, "name": "Fresh Coconut (น้ำมะพร้าว)", "price": 45.0, "category": "drinks"},
                {"id": 8, "name": "Mango Sticky Rice (ข้าวเหนียวมะม่วง)", "price": 90.0, "category": "desserts"},
                {"id": 9, "name": "Coconut Ice Cream (ไอติมกะทิ)", "price": 50.0, "category": "desserts"},
            ],
            "tables": [
                {"tableId": "T-01", "capacity": 2, "section": "Indoor", "status": "available", "currentOrderId": None},
                {"tableId": "T-02", "capacity": 4, "section": "Indoor", "status": "available", "currentOrderId": None},
                {"tableId": "T-03", "capacity": 4, "section": "Window", "status": "available", "currentOrderId": None},
                {"tableId": "T-04", "capacity": 6, "section": "Window", "status": "available", "currentOrderId": None},
                {"tableId": "T-05", "capacity": 4, "section": "Outdoor", "status": "available", "currentOrderId": None},
                {"tableId": "T-06", "capacity": 6, "section": "Outdoor", "status": "available", "currentOrderId": None},
                {"tableId": "VIP-01", "capacity": 10, "section": "VIP", "status": "available", "currentOrderId": None},
            ],
            "orders": [],
            "customers": [
                {"id": 1, "name": "Walk-in Guest", "phone": ""},
                {"id": 2, "name": "Somchai Prasert", "phone": "081-234-5678"},
                {"id": 3, "name": "Apinya Wong", "phone": "089-765-4321"},
            ],
            "next_order_id": 101,
        }
        self.save_all(default_data)

    def load_all(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            self._init_default_db()
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)

    def save_all(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_order(self, order_dict: Dict[str, Any]) -> None:
        data = self.load_all()
        data["orders"].append(order_dict)
        data["next_order_id"] = max(data.get("next_order_id", 101), order_dict.get("orderId", 100) + 1)
        self.save_all(data)

    def update_order_status(self, order_id: int, new_status: str) -> bool:
        data = self.load_all()
        for o in data["orders"]:
            if o.get("orderId") == order_id:
                o["status"] = new_status
                self.save_all(data)
                return True
        return False

    def get_summary_reports(self) -> Dict[str, Any]:
        data = self.load_all()
        orders = data.get("orders", [])
        completed = [o for o in orders if o.get("status") == "completed"]
        total_revenue = sum(float(o.get("total", 0)) for o in completed)

        item_counts: Dict[str, int] = {}
        for o in completed:
            for item in o.get("items", []):
                name = item.get("name", "Unknown")
                qty = int(item.get("quantity", 1))
                item_counts[name] = item_counts.get(name, 0) + qty

        popular_items = sorted(
            [{"name": k, "count": v} for k, v in item_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        return {
            "totalOrders": len(orders),
            "completedOrders": len(completed),
            "totalRevenue": round(total_revenue, 2),
            "popularItems": popular_items[:5],
            "activeTables": len([t for t in data.get("tables", []) if t.get("status") == "occupied"]),
        }
