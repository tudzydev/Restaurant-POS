# 🍽️ TableOne Restaurant POS: Master System Documentation

> **Specification-Driven, Full-Stack Restaurant Point of Sale & Management Platform**  
> *Consolidated System Architecture, Visual UML Models, Multi-Role User Experience, REST API Reference, and Verification Matrix.*

---

## 📑 Table of Contents
1. [Executive Overview](#1-executive-overview)
2. [Specification-Driven Domain Models & Invariants](#2-specification-driven-domain-models--invariants)
3. [Multi-Role Architecture & User Interfaces](#3-multi-role-architecture--user-interfaces)
4. [Unified UML Visual Models](#4-unified-uml-visual-models)
   - 4.1 [Use Case Diagram](#41-use-case-diagram)
   - 4.2 [Detailed Class Diagram](#42-detailed-class-diagram)
   - 4.3 [Sequence Diagram: Happy Path Order & Cash Tender](#43-sequence-diagram-happy-path-order--cash-tender)
   - 4.4 [Sequence Diagram: Payment Failure & Cancellation](#44-sequence-diagram-payment-failure--cancellation)
   - 4.5 [Sequence Diagram: Kitchen Display System (KDS) Bump Flow](#45-sequence-diagram-kitchen-display-system-kds-bump-flow)
   - 4.6 [Sequence Diagram: Table Floor Map Synchronization](#46-sequence-diagram-table-floor-map-synchronization)
5. [Complete REST API Specification](#5-complete-rest-api-specification)
6. [Operational User Guide by Role](#6-operational-user-guide-by-role)
   - 6.1 [Cashier & Waitstaff (Front of House)](#61-cashier--waitstaff-front-of-house)
   - 6.2 [Kitchen & Bar Staff (Back of House / KDS)](#62-kitchen--bar-staff-back-of-house--kds)
   - 6.3 [Restaurant Manager & Administration](#63-restaurant-manager--administration)
   - 6.4 [Customer Self-Order Kiosk (Guest UI)](#64-customer-self-order-kiosk-guest-ui)
7. [Hardware & Thermal Printing Integration](#7-hardware--thermal-printing-integration)
8. [Persistence Subsystem & JSON Database Schema](#8-persistence-subsystem--json-database-schema)
9. [Automated Acceptance Testing Suite (43 Tests)](#9-automated-acceptance-testing-suite-43-tests)
10. [Deployment & Operations](#10-deployment--operations)

---

## 1. Executive Overview

**TableOne Restaurant POS** is an enterprise-grade, specification-driven restaurant management system. Designed for high operational tempo, tactile ergonomics, and reliability, TableOne operates with **zero external runtime dependencies** (built strictly on Python 3 standard library and vanilla modern web technologies).

### Core Capabilities
- **High-Velocity Cashier Terminal**: Instant dish lookup (`/`), quick tender bank notes, live change calculation, and `@media print` 80mm thermal receipts.
- **Kitchen Display System (KDS)**: Real-time ticket board with elapsed prep timers, station status bump bar (`Pending` → `Cooking` → `Ready` → `Complete`), and cooking notes.
- **Customer Self-Ordering Kiosk**: Guest-facing touch kiosk allowing dine-in table ordering or takeaway, customized cooking preferences, and instant dispatch to the kitchen queue.
- **Executive Management & Analytics**: Menu catalog CRUD (dish additions, category & pricing adjustments, deletions), daily gross sales KPIs, Average Order Value (AOV), and popularity leaderboards.
- **Table Floor Management**: Real-time tracking of indoor, window, outdoor, and VIP table occupancy linked directly to active order IDs.
- **Polymorphic Payments**: Extensible payment hierarchy for Cash (with change logic), Credit Card (16-digit verification and masking), QR Code PromptPay, and Pay at Counter.

---

## 2. Specification-Driven Domain Models & Invariants

Core business rules are implemented as pure Python object-oriented domain classes:

### 2.1 Order State Machine Invariants
```mermaid
stateDiagram-v2
    [*] --> PENDING : createOrder(customer) / Kiosk Submit

    PENDING --> COOKING : kitchenBump() [Start Cooking]
    PENDING --> CONFIRMED : checkout() [items > 0]
    PENDING --> CANCELLED : cancel()

    COOKING --> READY : kitchenBump() [Mark Ready]
    COOKING --> CANCELLED : cancel()

    READY --> COMPLETED : kitchenBump() / serverComplete() [Served]
    CONFIRMED --> COMPLETED : complete() [payment == true]
    CONFIRMED --> CANCELLED : cancel()

    COMPLETED --> [*]
    CANCELLED --> [*]
```

1. **Non-Empty Cart Invariant**: An order cannot be checked out with zero items (`ValueError("Order is empty")`).
2. **Strict Mutation Guard**: Once an order transitions out of `PENDING` (into `CONFIRMED`, `COOKING`, or `COMPLETED`), calling `addItem()` or `removeItem()` raises `RuntimeError`.
3. **No Direct Completion**: Orders cannot transition directly from `PENDING` to `COMPLETED` without confirmation/checkout.
4. **Non-Reversible Completion**: Once marked `COMPLETED`, an order cannot be cancelled (`ValueError("Completed order cannot be cancelled")`).
5. **Strict Positive Quantity**: `OrderItem(menu_item, quantity)` enforces `quantity > 0`.
6. **7% Value-Added Tax (VAT)**: Tax is computed strictly as $\text{tax} = \text{subtotal} \times 0.07$ and grand total is $\text{subtotal} + \text{tax}$.

---

## 3. Multi-Role Architecture & User Interfaces

TableOne includes an interactive **Role Switcher** that immediately customizes views and user personas:

| Role | Operational Scope | Default View | Active Views Available |
| :--- | :--- | :--- | :--- |
| **🧑‍💼 Cashier / Waitstaff** | Front of House (FOH) | Point of Sale | POS Terminal, Table Map, Order History |
| **👨‍🍳 Kitchen / Bar Staff** | Back of House (BOH) | Kitchen Display | Kitchen Display System (KDS), Order History |
| **👔 Restaurant Manager** | Operations & Admin | Sales Analytics | Sales Analytics, Menu Manager, Table Map, POS, History |
| **📱 Customer / Guest** | Guest Self-Order | Guest Kiosk | Customer Self-Ordering Kiosk |

---

## 4. Unified UML Visual Models

### 4.1 Use Case Diagram

```mermaid
flowchart LR
    Customer([👤 Customer / Guest])
    Cashier([🧑‍💼 Cashier / Waitstaff])
    Manager([👔 Restaurant Manager])

    subgraph POS["TableOne Restaurant POS System"]
        UC1([View Menu Catalog])
        UC2([Select Dining Mode & Table])
        UC3([Create Order])
        UC4([Add / Modify Order Items])
        UC5([Calculate Total & 7% VAT])
        UC6([Process Payment])
        UC6_Cash([Pay by Cash & Compute Change])
        UC6_Card([Pay by Credit Card & Mask])
        UC6_QR([Pay by QR Code])
        UC7([Checkout & Complete Order])
        UC8([Print 80mm Thermal Receipt])
        UC9([Cancel Order])
        UC10([Manage Table Floor Map])
        UC11([Manage Menu Catalog])
        UC12([View Sales Analytics & Reports])
    end

    Customer --> UC1
    Customer --> UC2
    Customer --> UC3

    Cashier --> UC2
    Cashier --> UC3
    Cashier --> UC4
    Cashier --> UC6
    Cashier --> UC7
    Cashier --> UC8
    Cashier --> UC9
    Cashier --> UC10

    Manager --> UC10
    Manager --> UC11
    Manager --> UC12

    UC3 -.->|includes| UC4
    UC7 -.->|includes| UC5
    UC7 -.->|includes| UC6
    UC7 -.->|includes| UC8
    UC6 --> UC6_Cash
    UC6 --> UC6_Card
    UC6 --> UC6_QR
    UC9 -.->|extends| UC7
```

---

### 4.2 Detailed Class Diagram

```mermaid
classDiagram
    direction TB

    class Restaurant {
        -str __name
        -Menu __menu
        -list[Order] __orders
        +name: str
        +menu: Menu
        +orders: list[Order]
        +addMenuItem(item: MenuItem) void
        +createOrder(customer: Customer) Order
    }

    class TableStatus {
        <<enumeration>>
        AVAILABLE
        OCCUPIED
        RESERVED
    }

    class Table {
        -str __table_id
        -int __capacity
        -str __section
        -TableStatus __status
        -int __current_order_id
        +table_id: str
        +capacity: int
        +section: str
        +status: TableStatus
        +current_order_id: int
        +occupy(order_id: int) void
        +release() void
        +reserve() void
        +to_dict() dict
    }

    class Customer {
        -int __id
        -str __name
        -str __phone
        +id: int
        +name: str
        +phone: str
        +getInfo() str
    }

    class Menu {
        -list[MenuItem] __items
        +items: list[MenuItem]
        +addItem(menuItem: MenuItem) void
        +removeItem(itemId: int) bool
        +findItem(itemId: int) MenuItem
    }

    class MenuItem {
        -int __id
        -str __name
        -float __price
        -str __category
        +id: int
        +name: str
        +price: float
        +category: str
        +getPrice() float
    }

    class OrderItem {
        -MenuItem __menu_item
        -int __quantity
        +menu_item: MenuItem
        +quantity: int
        +calculate_subtotal() float
    }

    class OrderStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        COMPLETED
        CANCELLED
    }

    class Order {
        -int __orderId
        -Customer __customer
        -list[OrderItem] __items
        -OrderStatus __orderStatus
        +orderId: int
        +customer: Customer
        +items: list[OrderItem]
        +orderStatus: OrderStatus
        +addItem(menuItem: MenuItem, quantity: int) void
        +removeItem(itemId: int) void
        +calculateTotal() float
        +checkout() void
        +complete() void
        +cancel() void
    }

    class Payment {
        <<abstract>>
        #float _amount
        +amount: float
        +pay() bool
    }

    class CashPayment {
        -float __receivedAmount
        +receivedAmount: float
        +pay() bool
    }

    class CreditCardPayment {
        -str __cardNumber
        +cardNumber: str
        +pay() bool
    }

    class QRPayment {
        -str __transactionId
        +transactionId: str
        +pay() bool
    }

    class POSStorage {
        -str filepath
        +load_all() dict
        +save_all(data: dict) void
        +add_order(order_dict: dict) void
        +update_order_status(order_id: int, new_status: str) bool
        +get_summary_reports() dict
    }

    Restaurant "1" *-- "1" Menu : manages catalog
    Restaurant "1" *-- "0..*" Order : tracks orders
    Order "1" --> "1" Customer : placed by
    Order "1" *-- "0..*" OrderItem : contains
    OrderItem "1" --> "1" MenuItem : references
    Menu "1" *-- "0..*" MenuItem : contains
    Order --> OrderStatus : state enum
    Table --> TableStatus : state enum
    Payment <|-- CashPayment : implements
    Payment <|-- CreditCardPayment : implements
    Payment <|-- QRPayment : implements
    POSStorage ..> Order : persists
    POSStorage ..> Table : persists
```

---

### 4.3 Sequence Diagram: Happy Path Order & Cash Tender

```mermaid
sequenceDiagram
    autonumber
    actor Cashier
    participant UI as POS Terminal (Web)
    participant Server as HTTP Server (server.py)
    participant Rest as Restaurant
    participant Ord as Order
    participant Pay as CashPayment
    participant DB as POSStorage (JSON DB)

    Cashier->>UI: Select Dining Mode (Dine-in Table T-01)
    Cashier->>UI: Select Items (2x Fried Rice, 1x Iced Tea)
    UI->>UI: Calculate Live Subtotal (฿145.00) + 7% VAT (฿10.15) = ฿155.15
    Cashier->>UI: Click Checkout
    UI-->>Cashier: Display Payment Dialog (Cash Tab)
    Cashier->>UI: Enter Received Cash (฿200.00)
    UI->>UI: Display Change (฿44.85)
    Cashier->>UI: Click Confirm and Pay

    UI->>Server: POST /api/orders/checkout
    Server->>Rest: createOrder(customer)
    Rest->>Ord: instantiate Order(id, customer, PENDING)
    Server->>Ord: addItem(fried_rice, 2)
    Server->>Ord: addItem(iced_tea, 1)
    Server->>Ord: calculateTotal()
    Ord-->>Server: ฿145.00 (+ VAT = ฿155.15)

    Server->>Pay: CashPayment(155.15, 200.00).pay()
    Pay-->>Server: True (Payment Validated)

    Server->>Ord: checkout() -> State: CONFIRMED
    Server->>Ord: complete() -> State: COMPLETED
    Server->>DB: add_order(order_payload) and occupy table T-01
    DB-->>Server: Saved to pos_database.json
    Server-->>UI: 200 OK (order completed)

    UI-->>Cashier: Display Payment Successful and 80mm Receipt
    Cashier->>UI: Click Print Receipt
    UI-->>Cashier: Send 80mm Thermal Slip to Printer
```

---

### 4.4 Sequence Diagram: Payment Failure & Cancellation

```mermaid
sequenceDiagram
    autonumber
    actor Cashier
    participant UI as POS Terminal (Web)
    participant Server as HTTP Server (server.py)
    participant Rest as Restaurant
    participant Ord as Order
    participant Pay as CreditCardPayment

    Cashier->>UI: Click Checkout (Total: ฿155.15)
    Cashier->>UI: Select Credit Card Tab and Enter Invalid Card Number
    Cashier->>UI: Click Confirm and Pay

    UI->>Server: POST /api/orders/checkout
    Server->>Rest: createOrder(customer)
    Server->>Ord: addItem(menuItem, quantity)
    Server->>Pay: CreditCardPayment(155.15, invalidCard).pay()
    Pay-->>Server: False (Invalid card length != 16)

    Server->>Ord: cancel() -> State: CANCELLED
    Server-->>UI: 400 Bad Request (Payment failed - Order cancelled)
    UI-->>Cashier: Show Warning Banner: Payment Failed
```

---

### 4.5 Sequence Diagram: Kitchen Display System (KDS) Bump Flow

```mermaid
sequenceDiagram
    autonumber
    actor Guest as Customer / Kiosk
    actor Chef as Kitchen Chef
    participant UI as POS / KDS (Web Client)
    participant Server as HTTP Server (server.py)
    participant DB as POSStorage (JSON DB)

    Guest->>UI: Send Order to Kitchen (Table T-03, Note: "Less spicy")
    UI->>Server: POST /api/orders/checkout (status: pending, method: counter)
    Server->>DB: Record order in pos_database.json
    Server-->>UI: 200 OK (Order #104 Placed)

    Note over UI: KDS screen auto-refreshes with new yellow ticket
    Chef->>UI: Tap "🔥 Start Cooking" on Ticket #104
    UI->>Server: POST /api/orders/status {orderId: 104, status: "cooking"}
    Server->>DB: Update order status to cooking
    Server-->>UI: 200 OK (status: cooking)
    UI-->>Chef: Card turns blue (IN PREPARATION)

    Chef->>UI: Tap "✅ Mark Ready" on Ticket #104
    UI->>Server: POST /api/orders/status {orderId: 104, status: "ready"}
    Server->>DB: Update order status to ready
    Server-->>UI: 200 OK (status: ready)
    UI-->>Chef: Card turns green (READY FOR RUNNER)
```

---

### 4.6 Sequence Diagram: Table Floor Map Synchronization

```mermaid
sequenceDiagram
    autonumber
    actor Waiter as Waitstaff / Host
    participant UI as Table Map View
    participant Server as HTTP Server
    participant DB as POSStorage

    Waiter->>UI: Open Table Map Tab
    UI->>Server: GET /api/tables
    Server->>DB: load_all() tables
    DB-->>Server: Return 7 tables with occupancy status
    Server-->>UI: 200 OK with table list
    UI-->>Waiter: Render Visual Color-Coded Table Floor Plan

    Waiter->>UI: Click Seat Guests on Table T-03
    UI->>Server: POST /api/tables/status (tableId: T-03, status: occupied)
    Server->>DB: Update table status to occupied
    DB-->>Server: Persisted to database
    Server-->>UI: 200 OK (status updated)
    UI-->>Waiter: Card switches to OCCUPIED with Toast feedback
```

---

## 5. Complete REST API Specification

The TableOne server serves static assets and REST endpoints over HTTP on port `8000`:

| Endpoint | Method | Payload / Params | Status Codes | Description |
| :--- | :---: | :--- | :---: | :--- |
| `/api/menu` | `GET` | None | `200` | Lists all menu dishes with ID, name, price, and category. |
| `/api/menu` | `POST` | `{"name": str, "price": float, "category": str}` | `201`, `400` | Registers a new dish into the catalog and persistent database. |
| `/api/menu/:id` | `DELETE` | URL parameter `:id` | `200`, `404` | Discontinues and deletes dish from the menu catalog. |
| `/api/tables` | `GET` | None | `200` | Returns all 7 floor tables, capacities, sections, and occupancy. |
| `/api/tables/status` | `POST` | `{"tableId": str, "status": str}` | `200`, `404` | Updates table occupancy (`available`, `occupied`, `reserved`). |
| `/api/customers` | `GET` | None | `200` | Returns directory of registered customer profiles. |
| `/api/customers` | `POST` | `{"name": str, "phone": str}` | `201`, `400` | Adds customer to directory. |
| `/api/orders` | `GET` | None | `200` | Returns complete audit trail of active and completed orders. |
| `/api/orders/checkout` | `POST` | `{"customerName", "diningMode", "tableNumber", "notes", "items", "payment", "status"}` | `200`, `400` | Calculates totals + 7% VAT, validates tender, persists order. |
| `/api/orders/status` | `POST` | `{"orderId": int, "status": str}` | `200`, `404` | KDS status transition (`pending` → `cooking` → `ready` → `completed`). |
| `/api/reports/summary`| `GET` | None | `200` | Aggregated analytics: gross revenue, total completed orders, AOV, and top sellers. |

---

## 6. Operational User Guide by Role

### 6.1 Cashier & Waitstaff (Front of House)
- **Starting an Order**: Select Dining Mode (`🍽️ Dine-in` with table selector or `🥡 Takeaway`).
- **Assign Customer**: Click `👤 Guest Selector` for quick presets (*Walk-in*, *VIP Somchai*, *Apinya*) or type customer phone.
- **Search Dishes**: Tap dish cards or press **`/`** to jump straight to keyboard search.
- **Tender Options**:
  - *Cash*: Click `Exact`, `฿100`, `฿500`, or `฿1,000` to auto-calculate change.
  - *Credit Card*: Type 16 numeric digits (auto-masked).
  - *QR Code*: Verify PromptPay authorization code.
- **Receipts**: Click `🖨️ Print Receipt` to output an 80mm receipt, then `Start Next Order`.

### 6.2 Kitchen & Bar Staff (Back of House / KDS)
- **Live Ticket Monitoring**: Switch to **👨‍🍳 Kitchen** role. Tickets list order ID, table/takeaway status, elapsed timer, dish portions, and cooking notes.
- **Bump Actions**:
  - Unstarted tickets: Tap `🔥 Start Cooking`.
  - In-prep tickets: Tap `✅ Mark Ready`.
  - Plated tickets: Tap `🍽️ Served & Complete`.
- **Station Filtering**: Switch between `All Active`, `🔥 Pending`, `🍳 Cooking`, and `✅ Ready`.

### 6.3 Restaurant Manager & Administration
- **Sales Analytics (`📊 Reports`)**: Live gross sales, completed order tally, Average Order Value (AOV), and units sold by dish.
- **Menu Management (`🍴 Menu Manager`)**: Click `+ Add New Dish` to register dishes or click `🗑️ Delete` to remove discontinued items.
- **Table Floor Map (`🪑 Table Map`)**: Check table availability across Indoor, Window, Outdoor, and VIP sections.

### 6.4 Customer Self-Order Kiosk (Guest UI)
- **Guest Experience**: Switch to **📱 Kiosk** role.
- **Tray Building**: Tap category filters and tap `+ Add to Tray` on dish cards.
- **Special Cooking Requests**: Enter kitchen instructions in the notes field (*e.g., “No chili, extra crispy”*).
- **Direct Dispatch**: Tap `🚀 Send to Kitchen`. The order arrives immediately on the Kitchen KDS and reserves the selected table.

---

## 7. Hardware & Thermal Printing Integration

TableOne incorporates production-grade print stylesheets (`@media print`):
- **Printer Compatibility**: Epson TM-T88, Star Micronics TSP100, Sunmi POS terminals, and any standard 80mm thermal receipt printer.
- **Page Dimensions**: Fixed $80\text{mm}$ roll width with $72\text{mm}$ printable text boundaries.
- **Visual Optimization**: Screen chrome, sidebar, and buttons are automatically hidden. Monospace receipt typography renders crisp barcodes, VAT breakdown, and change calculations.

---

## 8. Persistence Subsystem & JSON Database Schema

System state is stored atomically in `data/pos_database.json`:

```json
{
  "menu": [
    { "id": 1, "name": "Fried Rice (ข้าวผัด)", "price": 60.0, "category": "mains" }
  ],
  "tables": [
    { "tableId": "T-01", "capacity": 2, "section": "Indoor", "status": "available", "currentOrderId": null }
  ],
  "orders": [
    {
      "orderId": 101,
      "customer": { "name": "Walk-in Guest", "phone": "" },
      "diningMode": "dinein",
      "tableNumber": "T-01",
      "notes": "Less spicy",
      "items": [{ "id": 1, "name": "Fried Rice (ข้าวผัด)", "price": 60.0, "quantity": 2, "subtotal": 120.0 }],
      "subtotal": 120.0,
      "tax": 8.4,
      "total": 128.4,
      "status": "completed",
      "paymentMethod": "Cash",
      "timestamp": "2026-09-09 14:00:00"
    }
  ],
  "customers": [
    { "id": 1, "name": "Walk-in Guest", "phone": "" }
  ],
  "next_order_id": 102
}
```

---

## 9. Automated Acceptance Testing Suite (43 Tests)

Every system invariant, state transition, and API endpoint is covered by automated specification tests:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

| Test Suite | File | Tests | Coverage |
| :--- | :--- | :---: | :--- |
| **Menu Specification** | `test_menu_spec.py` | 4 | Adding, removing, property encapsulation, missing items. |
| **Order Specification** | `test_order_spec.py` | 14 | Totals calculation, item removal, positive quantity, checkout guards, state invariants. |
| **Payment Specification** | `test_payment_spec.py` | 10 | Exact & sufficient cash, 16-digit card validation, card string cleaning, PromptPay QR tokens. |
| **E2E Flow Specification** | `test_e2e_flow_spec.py` | 3 | Full happy path flow, payment failure cancellation flow, sequential order ID generation. |
| **Full System Specification**| `test_full_system_spec.py` | 7 | Table allocation/release, persistence serialization, Menu CRUD, report metrics. |
| **Server Specification** | `test_server_spec.py` | 2 | HTTP REST API GET /api/menu and POST /api/orders/checkout. |
| **Multi-Role Specification**| `test_role_coverage_spec.py`| 3 | Customer Kiosk dispatch, Kitchen KDS bump lifecycle, Manager analytics & catalog CRUD. |
| **Total Passed** | **7 Test Suites** | **43** | **100% Passing Acceptance Rate** |

---

## 10. Deployment & Operations

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/tudzydev/Restaurant-POS.git
cd Restaurant-POS

# 2. Run automated test suite
python3 -m unittest discover -s tests -p "test_*.py" -v

# 3. Launch HTTP server (defaults to port 8000)
python3 server.py 8000
```
Open **`http://localhost:8000`** in Google Chrome, Safari, or on a tablet device.
