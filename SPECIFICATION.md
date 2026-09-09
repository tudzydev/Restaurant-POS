# Full System Specification: Restaurant Point of Sale (POS)

## 1. System Overview & Purpose

The **TableOne Restaurant POS System** is a full-stack, specification-driven point-of-sale platform. It connects restaurant floor operations, kitchen ticket workflows, table allocation, catalog management, and payment processing into a synchronized system.

---

## 2. Domain Model & Class Architecture

```mermaid
classDiagram
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
        +pay()* bool
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

    Restaurant "1" *-- "1" Menu : has
    Restaurant "1" *-- "0..*" Order : manages
    Order "1" --> "1" Customer : placed by
    Order "1" *-- "0..*" OrderItem : contains
    OrderItem "1" --> "1" MenuItem : references
    Menu "1" *-- "0..*" MenuItem : contains
    Payment <|-- CashPayment
    Payment <|-- CreditCardPayment
    Payment <|-- QRPayment
    POSStorage ..> Order : persists
    Table --> TableStatus
```

---

## 3. Order Lifecycle & State Machine Specification

```mermaid
stateDiagram-v2
    [*] --> PENDING : createOrder(customer)

    PENDING --> CONFIRMED : checkout() [items is not empty]
    PENDING --> CANCELLED : cancel()

    CONFIRMED --> COMPLETED : complete() [payment successful]
    CONFIRMED --> CANCELLED : cancel()

    COMPLETED --> [*]
    CANCELLED --> [*]
```

### Invariant Rules
1. **Empty Cart Checkout Block**: An order cannot be checked out with zero items. Raises `ValueError("Order is empty")`.
2. **Post-Checkout Mutation Lock**: Once an order is checked out (`CONFIRMED`) or completed, no items can be added or removed.
3. **Quantity Invariant**: Item quantities must be positive integers (`quantity > 0`).
4. **Table Allocation Lock**: Occupying an already occupied table by a different order raises `ValueError`.

---

## 4. Payment Specifications & Polymorphism

| Payment Method | Required Fields | Verification Contract | Success Criteria |
| :--- | :--- | :--- | :--- |
| **Cash** | `amount`, `receivedAmount` | Evaluates received tender vs total owed; computes exact change. | `receivedAmount >= amount` |
| **Credit Card** | `amount`, `cardNumber` | Strips formatting; validates exactly 16 numeric digits; masks output `****-****-****-XXXX`. | `len(digits) == 16 and digits.isdigit()` |
| **QR Code** | `amount`, `transactionId` | Validates transaction ID non-empty and non-whitespace. | `bool(transactionId.strip())` |

---

## 5. Full REST API Specification

| Endpoint | Method | Payload / Params | Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/menu` | `GET` | None | `list[MenuItem]` | Returns entire restaurant catalog. |
| `/api/menu` | `POST` | `{name, price, category}` | `MenuItem` (201) | Adds new dish to catalog & persistent DB. |
| `/api/menu/:id` | `DELETE` | Path `:id` | `{success: true}` (200) | Removes dish from menu. |
| `/api/tables` | `GET` | None | `list[Table]` | Returns all restaurant floor tables & statuses. |
| `/api/tables/status`| `POST` | `{tableId, status}` | `{success: true}` (200) | Updates table status (`available`/`occupied`). |
| `/api/customers` | `GET` | None | `list[Customer]` | Returns registered customer profiles. |
| `/api/customers` | `POST` | `{name, phone}` | `Customer` (201) | Registers customer profile. |
| `/api/orders` | `GET` | None | `list[Order]` | Returns full audit log of all orders. |
| `/api/orders/checkout` | `POST` | `{customerName, items, payment, diningMode, tableNumber}` | `{success, order}` (200) | Validates total, processes payment, persists order. |
| `/api/reports/summary` | `GET` | None | `{totalOrders, completedOrders, totalRevenue, popularItems}` | Real-time analytics report. |

---

## 6. End-to-End Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Cashier
    participant UI as Web POS (index.html)
    participant API as Backend (server.py)
    participant DB as Storage (pos_database.json)

    Cashier->>UI: Select Dining Mode (Dine-in / Takeaway)
    Cashier->>UI: Add Items to Cart
    Cashier->>UI: Click Checkout
    UI->>Cashier: Display Payment Dialog (Cash/Card/QR)
    Cashier->>UI: Enter Payment Tender
    UI->>API: POST /api/orders/checkout
    API->>API: Calculate Total + 7% VAT & Process Payment
    API->>DB: Save Order & Update Table Occupancy
    API-->>UI: 200 OK {success: true, order}
    UI->>Cashier: Render Printable 80mm Receipt
    UI->>UI: Refresh Tables & Sales Analytics
```

---

## 7. Automated Test Suite (40 Specification Tests)

All 40 acceptance criteria are validated automatically with `python3 -m unittest discover -s tests`:
- [`tests/test_menu_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_menu_spec.py): Menu addition, removal, and lookup specs.
- [`tests/test_order_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_order_spec.py): Order calculation, mutation guards, and state machine invariants.
- [`tests/test_payment_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_payment_spec.py): Cash, Card, and QR payment contracts.
- [`tests/test_e2e_flow_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_e2e_flow_spec.py): End-to-end integration workflows.
- [`tests/test_full_system_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_full_system_spec.py): Table allocation, persistence, menu CRUD, and report analytics.
- [`tests/test_server_spec.py`](file:///Users/mac/Desktop/workspace/Restaurant-POS/tests/test_server_spec.py): REST API contracts.
