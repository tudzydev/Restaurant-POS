# REST API Documentation

The TableOne Restaurant POS server exposes a JSON REST API on port `8000`.

Base URL: `http://localhost:8000/api`

---

## 1. Menu Management

### `GET /api/menu`
Retrieves all items currently in the restaurant catalog.

- **Status Code**: `200 OK`
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Fried Rice (ข้าวผัด)",
    "price": 60.0,
    "category": "mains"
  },
  {
    "id": 5,
    "name": "Iced Tea (ชาเย็น)",
    "price": 25.0,
    "category": "drinks"
  }
]
```

---

### `POST /api/menu`
Registers a new dish into the menu catalog and persists it.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "name": "Tom Kha Gai",
  "price": 130.0,
  "category": "mains"
}
```
- **Status Codes**:
  - `201 Created`: Item successfully added.
  - `400 Bad Request`: Missing name or invalid non-positive price.
- **Response**:
```json
{
  "id": 10,
  "name": "Tom Kha Gai",
  "price": 130.0,
  "category": "mains"
}
```

---

### `DELETE /api/menu/:id`
Deletes a menu item by numeric ID.

- **Status Codes**:
  - `200 OK`: Item removed.
  - `404 Not Found`: Item ID does not exist.
- **Response**:
```json
{
  "success": true,
  "deletedId": 10
}
```

---

## 2. Table Floor Management

### `GET /api/tables`
Returns the status of all restaurant floor tables.

- **Status Code**: `200 OK`
- **Response**:
```json
[
  {
    "tableId": "T-01",
    "capacity": 2,
    "section": "Indoor",
    "status": "available",
    "currentOrderId": null
  },
  {
    "tableId": "T-02",
    "capacity": 4,
    "section": "Indoor",
    "status": "occupied",
    "currentOrderId": 102
  }
]
```

---

### `POST /api/tables/status`
Updates table occupancy.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "tableId": "T-01",
  "status": "occupied"
}
```
- **Status Code**: `200 OK`
- **Response**:
```json
{
  "success": true,
  "tableId": "T-01",
  "status": "occupied"
}
```

---

## 3. Order Processing & Checkout

### `POST /api/orders/checkout`
Processes a complete customer order, validates pricing, calculates 7% VAT, validates and executes payment, and persists the transaction.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "customerName": "Somchai Prasert",
  "customerPhone": "081-234-5678",
  "diningMode": "dinein",
  "tableNumber": "T-01",
  "items": [
    { "id": 1, "quantity": 2 },
    { "id": 5, "quantity": 1 }
  ],
  "payment": {
    "method": "cash",
    "receivedAmount": 150.0
  }
}
```
- **Status Codes**:
  - `200 OK`: Payment successful, order completed and recorded.
  - `400 Bad Request`: Empty order, insufficient funds, or invalid card number.
- **Response**:
```json
{
  "success": true,
  "orderId": 101,
  "status": "completed",
  "total": 155.15,
  "order": {
    "orderId": 101,
    "customer": {
      "name": "Somchai Prasert",
      "phone": "081-234-5678"
    },
    "diningMode": "dinein",
    "tableNumber": "T-01",
    "items": [
      {
        "id": 1,
        "name": "Fried Rice (ข้าวผัด)",
        "price": 60.0,
        "quantity": 2,
        "subtotal": 120.0
      },
      {
        "id": 5,
        "name": "Iced Tea (ชาเย็น)",
        "price": 25.0,
        "quantity": 1,
        "subtotal": 25.0
      }
    ],
    "subtotal": 145.0,
    "tax": 10.15,
    "total": 155.15,
    "status": "completed",
    "paymentMethod": "Cash",
    "timestamp": "2026-09-09 14:00:00"
  }
}
```

---

## 4. Reports & Analytics

### `GET /api/reports/summary`
Returns real-time aggregated sales metrics.

- **Status Code**: `200 OK`
- **Response**:
```json
{
  "totalOrders": 12,
  "completedOrders": 12,
  "totalRevenue": 1642.50,
  "activeTables": 3,
  "popularItems": [
    { "name": "Fried Rice (ข้าวผัด)", "count": 18 },
    { "name": "Iced Tea (ชาเย็น)", "count": 14 },
    { "name": "Tom Yum Kung (ต้มยำกุ้ง)", "count": 8 }
  ]
}
```
