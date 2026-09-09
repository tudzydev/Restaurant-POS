# Architecture & Technical Design Document

## 1. Architectural Principles

The **TableOne Restaurant POS System** is architected around **Domain-Driven Design (DDD)** and **Specification-Driven Development (SDD)** principles:

1. **Explicit Domain Boundaries**: Core business rules (order totals, status transitions, payment validation, table allocations) are encapsulated purely in object-oriented domain classes with zero third-party dependencies.
2. **Polymorphic Extensibility**: Payment processing is structured using the Strategy / Subtype Polymorphism pattern, allowing new payment methods (e.g., Apple Pay, gift cards) to be introduced without modifying existing checkout routines.
3. **Fail-Closed State Invariants**: Orders cannot be mutated after checkout, empty orders cannot be checked out, completed orders cannot be cancelled, and item quantities must be strictly positive integers.
4. **Multi-Role User Experience**: Dedicated UI workflows tailored specifically for each restaurant persona: Front-of-House (Cashier/Waitstaff), Back-of-House (Kitchen Display System), Management (Analytics & Catalog), and Guests (Self-Ordering Kiosk).
5. **Resilient Persistence**: Lightweight file-backed JSON database (`storage.py`) providing zero-configuration data persistence across restarts with offline fallback on the frontend.

---

## 2. Multi-Role System Architecture

```mermaid
flowchart TD
    subgraph Users["Restaurant Operational Roles"]
        Cashier["🧑‍💼 Cashier / Waitstaff (FOH)"]
        Chef["👨‍🍳 Kitchen / Bar Staff (BOH)"]
        Manager["👔 Restaurant Manager"]
        Guest["📱 Customer / Guest (Kiosk)"]
    end

    subgraph Client["Presentation Layer (Vanilla HTML5 / CSS3 / ES6+)"]
        Shell["App Shell & Dynamic Role Switcher"]
        V_POS["POS Terminal View"]
        V_KDS["Kitchen Display System (KDS) View"]
        V_Kiosk["Customer Self-Ordering Kiosk View"]
        V_Tables["Table Floor Map View"]
        V_Menu["Menu Catalog Manager View"]
        V_Reports["Sales Analytics & Reports View"]
    end

    subgraph Server["Application Server (server.py)"]
        HTTPHandler["SimpleHTTPRequestHandler + Custom Router"]
        APIs["REST API Endpoints (/api/menu, /api/tables, /api/orders)"]
    end

    subgraph Domain["Domain Engine (Pure Python OOP)"]
        Rest["Restaurant & Menu (restaurant.py, menu.py)"]
        Orders["Order & OrderItem (orders.py, order_item.py)"]
        Payments["Payment Hierarchy (payment.py)"]
        Tables["Table & TableStatus (tables.py)"]
    end

    subgraph Persistence["Storage Subsystem (storage.py)"]
        JSONDB[("data/pos_database.json")]
    end

    Cashier --> V_POS
    Cashier --> V_Tables
    Chef --> V_KDS
    Manager --> V_Menu
    Manager --> V_Reports
    Guest --> V_Kiosk

    V_POS & V_KDS & V_Kiosk & V_Tables & V_Menu & V_Reports --> Shell
    Shell <-->|Fetch REST API| Server
    Server <--> Domain
    Server <--> Persistence
    Persistence <--> JSONDB
```

---

## 3. Domain Model Architecture

```mermaid
classDiagram
    direction TB

    class Restaurant {
        -str __name
        -Menu __menu
        -list[Order] __orders
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
        +occupy(order_id: int) void
        +release() void
        +reserve() void
        +to_dict() dict
    }

    class Customer {
        -int __id
        -str __name
        -str __phone
        +getInfo() str
    }

    class Menu {
        -list[MenuItem] __items
        +addItem(menuItem: MenuItem) void
        +removeItem(itemId: int) bool
        +findItem(itemId: int) MenuItem
    }

    class MenuItem {
        -int __id
        -str __name
        -float __price
        -str __category
        +getPrice() float
    }

    class OrderItem {
        -MenuItem __menu_item
        -int __quantity
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

    Restaurant "1" *-- "1" Menu
    Restaurant "1" *-- "0..*" Order
    Menu "1" *-- "0..*" MenuItem
    Order "1" *-- "0..*" OrderItem
    OrderItem "1" --> "1" MenuItem
    Order --> OrderStatus
    Table --> TableStatus
    Payment <|-- CashPayment
    Payment <|-- CreditCardPayment
    Payment <|-- QRPayment
    POSStorage ..> Order : persists
    POSStorage ..> Table : persists
```

---

## 4. Order Lifecycle & Kitchen State Machine

Orders adhere strictly to finite state transitions:

```mermaid
stateDiagram-v2
    [*] --> PENDING : createOrder(customer) / Guest Kiosk Submit

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

### Invariant Rules
- **Non-Empty Cart**: `checkout()` verifies `len(self.__items) > 0`; otherwise raises `ValueError("Order is empty")`.
- **Status Guards**: Direct transition from `PENDING` to `COMPLETED` is rejected; an order must be confirmed before completion.
- **Cancellation Lock**: `cancel()` rejects cancellation once an order reaches `OrderStatus.COMPLETED`.
- **Item Mutation Lock**: `addItem()` and `removeItem()` require `OrderStatus.PENDING`. Mutating locked orders raises `RuntimeError`.
- **Positive Quantity Invariant**: `OrderItem` validates `quantity > 0` on construction.

---

## 5. Payment Subsystem Design

All payment types inherit from the abstract base class `Payment`:

- **CashPayment**: Evaluates `receivedAmount >= amount`. Computes change `receivedAmount - amount`.
- **CreditCardPayment**: Sanitizes non-numeric characters and verifies standard 16-digit card strings. Masks card output as `****-****-****-XXXX`.
- **QRPayment**: Validates presence of a non-empty `transactionId`.
- **Counter Payment**: Dedicated checkout pathway enabling customer self-orders from tabletop kiosks to enter the kitchen queue for post-meal settlement.

---

## 6. Persistence Subsystem (`storage.py`)

The persistence engine manages file I/O for `data/pos_database.json`:
- **Auto-Initialization**: Missing or corrupted database files are automatically initialized with default seed menus and tables.
- **Atomic Serialization**: High-level atomic read/write using Python's standard `json` module.
- **Table Synchronization**: Table occupancy dynamically links to active order IDs and automatically releases when orders complete.
