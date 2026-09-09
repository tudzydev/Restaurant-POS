# 📐 TableOne Restaurant POS: UML Diagrams

This document contains the complete visual UML models for the TableOne Restaurant POS system, including **Use Case Diagrams**, **Class Diagrams**, and **Sequence Diagrams**.

---

## 1. Use Case Diagram

The use case diagram models the interactions between the system actors (**Customer**, **Cashier / Waitstaff**, **Restaurant Manager**, and **Kitchen / Bar Staff**) and the primary business functions of the POS system.

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

## 2. Detailed Class Diagram

The class diagram captures the object-oriented structure of the domain model, encapsulation, inheritance hierarchies, and data persistence associations.

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

## 3. Sequence Diagrams

### 3.1 Successful Order, Cash Payment & Completion (Happy Path)

This diagram details the primary order lifecycle from creation through item aggregation, total computation, cash tendering with change calculation, receipt rendering, and database persistence.

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

### 3.2 Failed Payment & Order Cancellation (Alternative Path)

This diagram illustrates the error-handling flow when a payment tender fails (e.g., insufficient cash or invalid credit card number).

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

### 3.3 Table Floor Management Sequence

This diagram shows how table occupancy is updated and synchronized between the UI, server, and persistent database.

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
