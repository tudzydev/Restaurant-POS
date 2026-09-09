# 📖 Cashier & Staff Operational Manual

Welcome to the **TableOne Restaurant POS** User Guide. This manual walks through all daily cashier, kitchen, and manager workflows.

---

## 1. Getting Started

1. Open your browser and navigate to:
   👉 **`http://localhost:8000`**
2. Ensure the bottom-left indicator shows **`🟢 Ready (Online)`**.

---

## 2. Taking an Order (POS Terminal)

### Step 1: Select Dining Type
At the top of the right-hand panel, select the guest's dining preference:
- **🍽️ Dine-in**: Choose the assigned table (`Table 01` – `Table 06` or `VIP Room 01`).
- **🥡 Takeaway**: For pickup and to-go bags.

### Step 2: Add Customer Information
- Click the **`👤 Guest Selector`** button.
- Choose a quick preset (e.g., *Walk-in Guest*, *Somchai Prasert*, *Apinya Wong*) or type a custom customer name and phone number.

### Step 3: Browse and Add Items
- Tap or click any dish card on the left to add 1 unit to the cart.
- **Filter by Category**: Tap `🍜 Mains`, `🥤 Drinks`, or `🍨 Desserts`.
- **Search**: Type in the search bar or press **`/`** on your keyboard to instantly find dishes by name.
- **Adjust Quantity**: Use the **`+`** and **`−`** buttons in the cart to change portions. Tap **`✕`** to remove a dish.

---

## 3. Processing Payment & Completing Orders

When all dishes are selected, click **`Checkout (฿XX.XX) →`** or press **`Enter`**.

### Method A: Cash Payment 💵
1. The Cash tab automatically opens with the exact total selected.
2. Enter the cash handed over by the customer, or click one of the quick note presets:
   - **`Exact`** | **`฿100`** | **`฿500`** | **`฿1,000`**
3. The screen instantly computes change.
4. If underpaid, an alert blocks completion until sufficient tender is entered.
5. Click **`Confirm & Pay`** or press **`Enter`**.

### Method B: Credit Card Payment 💳
1. Switch to the **`💳 Credit Card`** tab.
2. Type or swipe the 16-digit card number. Spaces and hyphens are automatically handled.
3. Click **`Confirm & Pay`**.

### Method C: QR Code Payment 📱
1. Switch to the **`📱 QR Code`** tab.
2. The guest scans the PromptPay QR on screen.
3. Confirm the transaction authentication code.
4. Click **`Confirm & Pay`**.

---

## 4. Receipts & Printing

Once payment succeeds, the **Payment Successful** modal automatically displays:
- Customer Name & Order ID
- Dining Mode (e.g., *Dine-in Table 03* or *Takeaway*)
- Itemized breakdown, Subtotal, 7% VAT, and Total Paid
- Change given (for cash transactions)

Click **`🖨️ Print Receipt`** to send the order directly to an attached **80mm thermal receipt printer**.

---

## 5. Table Floor Map

1. Click **`🪑 Table Map`** in the left sidebar.
2. Color-coded cards show:
   - **`🟢 Available`**: Ready for seating. Click **`Seat Guests`** to mark it occupied.
   - **`🔴 Occupied`**: Shows the active order ID. When guests depart, click **`Mark Available`** to free the table.

---

## 6. Menu Catalog Management

1. Click **`🍴 Menu Manager`** in the left sidebar.
2. **Add New Dish**: Click **`+ Add New Dish`**, enter the item name, price (฿), and category, and click **`Add Item`**.
3. **Delete Dish**: Click **`🗑️ Delete`** next to any item to discontinue it.

---

## 7. Keyboard Shortcuts Cheat Sheet

| Key | Action |
| :--- | :--- |
| **`/`** | Focus the search bar instantly |
| **`Esc`** | Close any active modal or dialog |
| **`Enter`** | Submit and confirm payment in the checkout dialog |
