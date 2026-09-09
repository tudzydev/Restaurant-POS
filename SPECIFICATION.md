# System Specification: Restaurant Point of Sale (POS)

## 1. System Overview & Purpose

The **Restaurant POS System** is an object-oriented point-of-sale domain model designed to handle customer orders, menu catalog management, bill calculation, and multi-channel payment processing (Cash, Credit Card, and QR Code).

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
        +id: int
        +name: str
        +price: float
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

    Restaurant "1" *-- "1" Menu : has
    Restaurant "1" *-- "0..*" Order : manages
    Order "1" --> "1" Customer : placed by
    Order "1" *-- "0..*" OrderItem : contains
    OrderItem "1" --> "1" MenuItem : references
    Menu "1" *-- "0..*" MenuItem : contains
    Payment <|-- CashPayment
    Payment <|-- CreditCardPayment
    Payment <|-- QRPayment
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

### State Transition Invariants
1. **`PENDING` $\to$ `CONFIRMED` via `checkout()`**:
   - **Pre-condition**: Order items list must not be empty (`len(items) > 0`).
   - **Pre-condition**: Current status must be `OrderStatus.PENDING`.
   - **Post-condition**: Status changes to `OrderStatus.CONFIRMED`.
   - **Error Handling**: Raises `ValueError("Order is empty")` or `ValueError("Order cannot be checked out")`.

2. **`CONFIRMED` $\to$ `COMPLETED` via `complete()`**:
   - **Pre-condition**: Current status must be `OrderStatus.CONFIRMED`.
   - **Post-condition**: Status changes to `OrderStatus.COMPLETED`.
   - **Error Handling**: Raises `ValueError("Order must be confirmed first")` if invoked in any other state.

3. **Any non-completed state $\to$ `CANCELLED` via `cancel()`**:
   - **Pre-condition**: Current status must **not** be `OrderStatus.COMPLETED`.
   - **Post-condition**: Status changes to `OrderStatus.CANCELLED`.
   - **Error Handling**: Raises `ValueError("Completed order cannot be cancelled")` if order is already completed.

4. **Order Mutation Invariants (`addItem`, `removeItem`)**:
   - **Pre-condition**: Order status must be strictly `OrderStatus.PENDING`. Cannot mutate items once checked out, completed, or cancelled.
   - **Quantity Invariant**: Item quantity must be an integer strictly greater than zero (`quantity > 0`). Raises `ValueError` otherwise.

---

## 4. Payment Specifications & Subtype Polymorphism

All payment methods inherit from the abstract base class `Payment` and implement `pay() -> bool`.

| Payment Type | Required Fields | Validation & Execution Rule | Success Condition |
| :--- | :--- | :--- | :--- |
| **CashPayment** | `amount: float`<br>`receivedAmount: float` | Compares received cash to total owed. Computes change: `receivedAmount - amount`. | `receivedAmount >= amount` |
| **CreditCardPayment** | `amount: float`<br>`cardNumber: str` | Strips whitespace/hyphens. Checks for exactly 16 numeric digits. Masks card (`****-****-****-XXXX`). | `len(cleaned) == 16 and cleaned.isdigit()` |
| **QRPayment** | `amount: float`<br>`transactionId: str` | Validates transaction ID non-empty and non-whitespace. | `bool(transactionId.strip())` |

---

## 5. End-to-End Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Cashier / System
    participant R as Restaurant
    participant C as Customer
    participant M as Menu
    participant O as Order
    participant P as Payment (Cash/Card/QR)

    Staff->>R: createOrder(customer)
    R->>O: instantiate Order(id, customer, PENDING)
    Staff->>O: addItem(menuItem, quantity)
    O->>O: append OrderItem(menuItem, quantity)
    Staff->>O: calculateTotal()
    O-->>Staff: total amount
    Staff->>P: pay()
    alt Payment Succeeded
        P-->>Staff: True (Receipt/Change displayed)
        Staff->>O: checkout() -> status: CONFIRMED
        Staff->>O: complete() -> status: COMPLETED
    else Payment Failed
        P-->>Staff: False (Error message)
        Staff->>O: cancel() -> status: CANCELLED
    end
```

---

## 6. Specification-Driven Acceptance Criteria (BDD / Test Matrix)

### Feature 1: Menu Management
- **Scenario 1.1**: Adding item to menu
  - **Given** an empty Menu
  - **When** `addItem(MenuItem(1, "Fried Rice", 60.00))` is called
  - **Then** `findItem(1)` returns the item and `items` count equals 1.
- **Scenario 1.2**: Removing existing item
  - **Given** a Menu with item ID 1
  - **When** `removeItem(1)` is called
  - **Then** method returns `True` and `findItem(1)` returns `None`.

### Feature 2: Order Computation
- **Scenario 2.1**: Subtotal calculation
  - **Given** a `MenuItem` with price 60.00 and quantity 2
  - **When** `calculate_subtotal()` is called on `OrderItem`
  - **Then** subtotal is `120.00`.
- **Scenario 2.2**: Order total calculation
  - **Given** an Order with 2 Fried Rice (60.00 ea) and 1 Iced Tea (25.00 ea)
  - **When** `order.calculateTotal()` is executed
  - **Then** total is `145.00`.

### Feature 3: Order State Enforcement
- **Scenario 3.1**: Empty order checkout rejection
  - **Given** an order with 0 items
  - **When** `order.checkout()` is called
  - **Then** `ValueError("Order is empty")` is raised.
- **Scenario 3.2**: Direct completion rejection
  - **Given** an order in `PENDING` status
  - **When** `order.complete()` is called
  - **Then** `ValueError("Order must be confirmed first")` is raised.
- **Scenario 3.3**: Completed order cancellation rejection
  - **Given** an order in `COMPLETED` status
  - **When** `order.cancel()` is called
  - **Then** `ValueError("Completed order cannot be cancelled")` is raised.

### Feature 4: Payment Verification
- **Scenario 4.1**: Insufficient cash payment
  - **Given** total amount `100.00` and cash received `80.00`
  - **When** `CashPayment.pay()` is called
  - **Then** returns `False`.
- **Scenario 4.2**: Valid credit card
  - **Given** card number `"1234-5678-9012-3456"` and amount `100.00`
  - **When** `CreditCardPayment.pay()` is called
  - **Then** returns `True` and logs masked card number.
