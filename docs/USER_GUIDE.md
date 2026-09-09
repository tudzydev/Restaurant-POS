# 📖 TableOne Restaurant POS: Complete Operational Manual

Welcome to the **TableOne Restaurant POS** User Guide. This manual explains the end-to-end workflows for all four restaurant operational roles: **Cashier / Waitstaff**, **Kitchen Staff (KDS)**, **Restaurant Manager**, and **Customer Self-Order Guests**.

---

## 🎭 1. Interactive Role Switcher

TableOne features a unified interface that adapts seamlessly to whichever role you are currently fulfilling. In the left-hand sidebar under **Active Role**, tap any of the four role buttons:

- **🧑‍💼 Cashier**: Activates front-of-house order terminal, quick tender, table assignment, and receipt printing.
- **👨‍🍳 Kitchen**: Opens the live Kitchen Display System (KDS) bump bar with prep timers and cooking queues.
- **👔 Manager**: Unlocks daily sales analytics, revenue reports, bestsellers leaderboards, and menu editing.
- **📱 Kiosk**: Enters guest self-ordering mode for tabletop tablets or walk-up kiosk stands.

---

## 🧑‍💼 2. Role 1: Cashier & Waitstaff (Front of House)

### Step 1: Select Dining Mode & Table
At the top of the right-hand order panel:
- **🍽️ Dine-in**: Pick the assigned table (`T-01` through `T-06` or `VIP-01`).
- **🥡 Takeaway**: Marks the order for pickup packaging.

### Step 2: Set Customer Profile
- Click **`👤 Guest Selector`**.
- Choose a quick preset (*Walk-in Guest*, *Somchai Prasert*, *Apinya Wong*) or type a custom customer name and phone number.

### Step 3: Browse and Add Items
- Tap any dish card in the menu grid to add 1 portion to the cart.
- **Category Filter**: Quickly jump between `🍜 Mains`, `🥤 Drinks`, and `🍨 Desserts`.
- **Search**: Press **`/`** on your keyboard to focus the search bar and type dish names.
- **Quantity Adjustments**: Use **`+`** and **`−`** steppers in the cart. Tap **`Clear`** to reset the cart.

### Step 4: Checkout & Polymorphic Payment
Click **`Checkout (฿XX.XX) →`** or press **`Enter`**:

1. **Cash Payment 💵**:
   - Tap preset bank note buttons (**`Exact`**, **`฿100`**, **`฿500`**, **`฿1,000`**) or type amount received.
   - The screen instantly calculates the exact change to return to the customer.
   - Click **`Confirm & Pay`**.
2. **Credit Card 💳**:
   - Switch to the **Credit Card** tab.
   - Enter the 16-digit card number (auto-formatted with spaces). Click **`Confirm & Pay`**.
3. **QR Code / PromptPay 📱**:
   - Switch to the **QR Code** tab.
   - Guest scans the PromptPay QR code; cashier verifies the transaction reference code and clicks **`Confirm & Pay`**.

### Step 5: 80mm Thermal Receipt Printing
- Once payment is confirmed, the **Payment Successful** modal displays the itemized receipt with 7% VAT.
- Click **`🖨️ Print Receipt`** to generate the thermal slip formatted for 80mm roll printers.
- Click **`Start Next Order`** to immediately begin the next sale.

---

## 👨‍🍳 3. Role 2: Kitchen Display System (KDS / Back of House)

Switch to the **👨‍🍳 Kitchen** role or select **`🍳 Kitchen Display (KDS)`** in the navigation menu.

### Ticket Board Anatomy
Each incoming kitchen ticket contains:
- **Header**: Order Number, Dining Mode (`Dine-in Table T-XX` vs `Takeaway`), and Customer Name.
- **Elapsed Timer**: Timestamp displaying when the ticket arrived.
- **Item Checklist**: Portions and dish names (e.g. `2x Pad Thai`, `1x Tom Yum Kung`).
- **Special Cooking Notes**: Displayed in prominent yellow callouts (e.g. *“Extra spicy, no cilantro, less ice”*).

### Ticket Lifecycle & Bump Bar
Kitchen staff advance orders through their lifecycle with a single touch:
1. **🔥 Pending (New Orders)**:
   - Order has just arrived from cashier or customer self-order kiosk.
   - Action: Tap **`🔥 Start Cooking`** → status changes to **`cooking`**.
2. **🍳 Cooking (In Preparation)**:
   - Dishes are actively being prepared on stations.
   - Action: Tap **`✅ Mark Ready`** → status changes to **`ready`**.
3. **✅ Ready (Plated)**:
   - Food is plated and waiting for waitstaff pickup or counter collection.
   - Action: Tap **`🍽️ Served & Complete`** → status transitions to **`completed`** and the ticket clears from the active board.

### Station Filters
Use the header filter pills to view:
- **`All Active`**: Displays all ongoing tickets.
- **`🔥 Pending`**: Shows only unstarted orders.
- **`🍳 Cooking`**: Shows orders currently in prep.
- **`✅ Ready`**: Shows plated orders ready for runners.
- **`🔄 Refresh`**: Instantly synchronizes tickets with the server.

---

## 👔 4. Role 3: Restaurant Manager (Admin & Operations)

Switch to the **👔 Manager** role to access executive overview panels.

### Sales Analytics & KPIs
Select **`📊 Sales Analytics`** to monitor:
- **Gross Revenue**: Live total of all completed sales.
- **Completed Orders**: Daily order count.
- **Average Order Value (AOV)**: Revenue per completed transaction.
- **Top-Selling Dishes**: Leaderboard of popular dishes with total units sold.

### Menu Catalog Manager
Select **`🍴 Menu Manager`**:
- **Add New Dish**: Click **`+ Add New Dish`**, specify dish name, price in THB (฿), and category (`Mains`, `Drinks`, `Desserts`), and click **`Add Item`**.
- **Discontinue Dish**: Click **`🗑️ Delete`** on any item to remove it from the menu across all terminals and kiosks.

### Table Floor Map
Select **`🪑 Table Map`**:
- Live view of 7 floor tables (`T-01` to `T-06` and `VIP-01`).
- Card displays section (*Indoor*, *Window*, *Outdoor*, *VIP*) and guest seating capacity.
- Tap **`Seat Guests`** / **`Mark Available`** to manually toggle table occupancy.

---

## 📱 5. Role 4: Customer Self-Ordering Kiosk (Guest UI)

Switch to the **📱 Kiosk** role or select **`Customer Kiosk`**:

1. **Dining Preference**: Select **`🍽️ Dine-in`** (with table picker) or **`🥡 Takeaway`**.
2. **Guest Name**: Optionally enter guest name (e.g., *“Alice”*).
3. **Browse Catalog**: Large, appetizing dish cards with prices and categories. Tap **`+ Add to Tray`** to select items.
4. **Special Instructions**: Type cooking instructions in the tray notes box (e.g., *“Vegetarian, no fish sauce, less sweet”*).
5. **Send Order to Kitchen**:
   - Tap **`🚀 Send to Kitchen`**.
   - The order is submitted as `pending` and immediately appears as a live ticket on the **Kitchen Display System (KDS)**!
   - Payment can be settled post-meal at the cashier counter or via PromptPay QR.

---

## ⌨️ 6. Keyboard Shortcuts Reference

| Shortcut | Context | Function |
| :--- | :--- | :--- |
| **`/`** | POS Screen | Jump cursor directly to search input |
| **`Esc`** | Any Screen | Close active modal dialog or dismiss search |
| **`Enter`** | Checkout Dialog | Confirm and finalize payment submission |
| **`Tab`** | Forms | Navigate between inputs and quick payment options |

---

## 🖨️ 7. Thermal Receipt Layout

TableOne includes built-in CSS print styling (`@media print`):
- Strips screen chrome, navigation bars, and buttons.
- Constrains layout to standard **80mm thermal receipt width** ($72\text{mm}$ printable area).
- High-contrast black-on-white monospace text with clean divider rules for thermal print heads.
