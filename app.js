/**
 * Restaurant POS - Frontend Application Engine
 * Implements Specification-Driven UI & State Machine
 */

(function () {
  "use strict";

  // --- Initial State & Seed Data ---
  const DEFAULT_MENU_ITEMS = [
    { id: 1, name: "Fried Rice (ข้าวผัด)", price: 60.0, category: "mains", icon: "🍛" },
    { id: 2, name: "Pad Thai (ผัดไทย)", price: 80.0, category: "mains", icon: "🍜" },
    { id: 3, name: "Green Curry (แกงเขียวหวาน)", price: 120.0, category: "mains", icon: "🍲" },
    { id: 4, name: "Tom Yum Kung (ต้มยำกุ้ง)", price: 150.0, category: "mains", icon: "🦐" },
    { id: 5, name: "Iced Tea (ชาเย็น)", price: 25.0, category: "drinks", icon: "🧋" },
    { id: 6, name: "Thai Milk Tea (ชาไทย)", price: 35.0, category: "drinks", icon: "🥤" },
    { id: 7, name: "Fresh Coconut (น้ำมะพร้าว)", price: 45.0, category: "drinks", icon: "🥥" },
    { id: 8, name: "Mango Sticky Rice (ข้าวเหนียวมะม่วง)", price: 90.0, category: "desserts", icon: "🥭" },
    { id: 9, name: "Coconut Ice Cream (ไอติมกะทิ)", price: 50.0, category: "desserts", icon: "🍨" }
  ];

  const state = {
    menuItems: [...DEFAULT_MENU_ITEMS],
    orderSequence: 101,
    activeOrder: {
      orderId: 101,
      customer: { name: "Walk-in Guest", phone: "" },
      diningMode: "dinein", // "dinein" | "takeaway"
      tableNumber: "T-01",
      items: [], // Array of { menuItem, quantity }
      status: "PENDING"
    },
    ordersHistory: [],
    tables: [
      { tableId: "T-01", capacity: 2, section: "Indoor", status: "available", currentOrderId: null },
      { tableId: "T-02", capacity: 4, section: "Indoor", status: "available", currentOrderId: null },
      { tableId: "T-03", capacity: 4, section: "Window", status: "available", currentOrderId: null },
      { tableId: "T-04", capacity: 6, section: "Window", status: "available", currentOrderId: null },
      { tableId: "T-05", capacity: 4, section: "Outdoor", status: "available", currentOrderId: null },
      { tableId: "T-06", capacity: 6, section: "Outdoor", status: "available", currentOrderId: null },
      { tableId: "VIP-01", capacity: 10, section: "VIP", status: "available", currentOrderId: null }
    ],
    selectedCategory: "all",
    searchQuery: "",
    paymentMethod: "cash"
  };

  // --- DOM Elements ---
  const el = {
    menuGrid: document.getElementById("menu-grid"),
    categoryPills: document.getElementById("category-pills"),
    searchInput: document.getElementById("search-input"),
    btnClearSearch: document.getElementById("btn-clear-search"),
    btnModeDinein: document.getElementById("btn-mode-dinein"),
    btnModeTakeaway: document.getElementById("btn-mode-takeaway"),
    tableSelectorRow: document.getElementById("table-selector-row"),
    selectTable: document.getElementById("select-table"),
    cartContainer: document.getElementById("cart-container"),
    emptyCartView: document.getElementById("empty-cart-view"),
    cartItemsList: document.getElementById("cart-items-list"),
    cartItemCount: document.getElementById("cart-item-count"),
    summarySubtotal: document.getElementById("summary-subtotal"),
    summaryTax: document.getElementById("summary-tax"),
    summaryTotal: document.getElementById("summary-total"),
    btnCheckout: document.getElementById("btn-checkout"),
    btnCheckoutAmount: document.getElementById("btn-checkout-amount"),
    btnClearOrder: document.getElementById("btn-clear-order"),
    orderLabel: document.getElementById("order-label"),
    headerOrderId: document.getElementById("header-order-id"),
    orderStatusBadge: document.getElementById("order-status-badge"),
    selectedCustomerName: document.getElementById("selected-customer-name"),
    selectedCustomerPhone: document.getElementById("selected-customer-phone"),
    statCustomerName: document.getElementById("stat-customer-name"),
    statRevenue: document.getElementById("stat-revenue"),
    statOrders: document.getElementById("stat-orders"),
    historyCount: document.getElementById("history-count"),
    currentDate: document.getElementById("current-date"),
    viewPos: document.getElementById("view-pos"),
    viewHistory: document.getElementById("view-history"),
    viewTables: document.getElementById("view-tables"),
    tablesGrid: document.getElementById("tables-grid"),
    viewMenuMgmt: document.getElementById("view-menu-mgmt"),
    menuMgmtTableBody: document.getElementById("menu-mgmt-table-body"),
    viewReports: document.getElementById("view-reports"),
    reportTotalRev: document.getElementById("report-total-rev"),
    reportCompletedOrders: document.getElementById("report-completed-orders"),
    reportAov: document.getElementById("report-aov"),
    reportBestsellersList: document.getElementById("report-bestsellers-list"),
    historyTableBody: document.getElementById("history-table-body"),
    emptyHistoryView: document.getElementById("empty-history-view"),

    // Modals
    modalBackdrop: document.getElementById("modal-backdrop"),
    modalPayment: document.getElementById("modal-payment"),
    modalCustomer: document.getElementById("modal-customer"),
    modalReceipt: document.getElementById("modal-receipt"),
    modalNewItem: document.getElementById("modal-new-item"),

    // Payment fields
    paymentDueAmount: document.getElementById("payment-due-amount"),
    cashReceivedInput: document.getElementById("cash-received-input"),
    cashChangeAmount: document.getElementById("cash-change-amount"),
    cashError: document.getElementById("cash-error"),
    cardNumberInput: document.getElementById("card-number-input"),
    cardError: document.getElementById("card-error"),
    qrTxnInput: document.getElementById("qr-txn-input"),
    qrError: document.getElementById("qr-error"),
    btnConfirmPayment: document.getElementById("btn-confirm-payment"),

    // Receipt fields
    receiptOrderId: document.getElementById("receipt-order-id"),
    receiptCustomer: document.getElementById("receipt-customer"),
    receiptDiningMode: document.getElementById("receipt-dining-mode"),
    receiptTimestamp: document.getElementById("receipt-timestamp"),
    receiptItemsList: document.getElementById("receipt-items-list"),
    receiptSubtotal: document.getElementById("receipt-subtotal"),
    receiptTax: document.getElementById("receipt-tax"),
    receiptTotal: document.getElementById("receipt-total"),
    receiptPaymentMethod: document.getElementById("receipt-payment-method"),
    receiptChangeRow: document.getElementById("receipt-change-row"),
    receiptChange: document.getElementById("receipt-change"),

    // Toast
    toast: document.getElementById("toast")
  };

  // --- Helper Functions ---
  const formatMoney = (val) => `฿${Number(val || 0).toFixed(2)}`;

  function showToast(message) {
    if (!el.toast) return;
    el.toast.textContent = message;
    el.toast.classList.add("show");
    setTimeout(() => {
      el.toast.classList.remove("show");
    }, 2800);
  }

  function calculateTotals() {
    const subtotal = state.activeOrder.items.reduce(
      (sum, row) => sum + row.menuItem.price * row.quantity,
      0
    );
    const tax = subtotal * 0.07; // 7% VAT
    const grandTotal = subtotal + tax;
    return { subtotal, tax, grandTotal };
  }

  // --- Category Inferrer & Safe Formatter ---
  function getItemCategory(item) {
    if (!item) return "mains";
    if (typeof item.category === "string" && item.category.trim()) {
      return item.category.trim().toLowerCase();
    }
    const name = String(item.name || "").toLowerCase();
    if (
      name.includes("tea") ||
      name.includes("drink") ||
      name.includes("water") ||
      name.includes("coconut") ||
      name.includes("ชา") ||
      name.includes("น้ำ")
    ) {
      return "drinks";
    }
    if (
      name.includes("ice cream") ||
      name.includes("mango") ||
      name.includes("sweet") ||
      name.includes("dessert") ||
      name.includes("ไอติม") ||
      name.includes("เหนียว")
    ) {
      return "desserts";
    }
    return "mains";
  }

  // --- Render Functions ---

  function renderMenu() {
    if (!el.menuGrid) el.menuGrid = document.getElementById("menu-grid");
    if (!el.menuGrid) return;

    const rawQuery = state.searchQuery || "";
    const cleanQuery = typeof rawQuery === "string" ? rawQuery.trim().toLowerCase() : "";
    const selectedCat = (state.selectedCategory || "all").toLowerCase();
    const items = Array.isArray(state.menuItems) ? state.menuItems : [];

    const filtered = items.filter((item) => {
      if (!item) return false;
      const itemCat = getItemCategory(item);
      const matchCat = selectedCat === "all" || itemCat === selectedCat;
      const itemName = String(item.name || "").toLowerCase();
      const matchSearch = !cleanQuery || itemName.includes(cleanQuery);
      return Boolean(matchCat && matchSearch);
    });

    el.menuGrid.innerHTML = "";
    if (filtered.length === 0) {
      el.menuGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; color: var(--muted); padding: 40px 0;">
          <p style="font-size: 16px; margin-bottom: 6px;">🔍 No items found</p>
          <small>Try choosing "All Items" or searching with another keyword.</small>
        </div>
      `;
      return;
    }

    filtered.forEach((item) => {
      const categoryLabel = getItemCategory(item);
      const card = document.createElement("div");
      card.className = "menu-card";
      card.setAttribute("role", "button");
      card.tabIndex = 0;
      card.innerHTML = `
        <div class="menu-card-top">
          <span class="dish-icon">${item.icon || (categoryLabel === "drinks" ? "🥤" : categoryLabel === "desserts" ? "🍨" : "🍲")}</span>
          <span class="menu-card-badge">${categoryLabel}</span>
        </div>
        <div class="menu-card-body">
          <h4>${item.name || "Unnamed Item"}</h4>
        </div>
        <div class="menu-card-bottom">
          <span class="dish-price">${formatMoney(item.price)}</span>
          <span class="add-pill">+</span>
        </div>
      `;
      card.addEventListener("click", () => addItemToOrder(item));
      el.menuGrid.appendChild(card);
    });
  }

  function renderCart() {
    const items = state.activeOrder.items;
    const count = items.reduce((total, i) => total + i.quantity, 0);
    el.cartItemCount.textContent = `${count} ${count === 1 ? "item" : "items"}`;

    if (items.length === 0) {
      el.emptyCartView.style.display = "flex";
      el.cartItemsList.style.display = "none";
      el.btnCheckout.disabled = true;
    } else {
      el.emptyCartView.style.display = "none";
      el.cartItemsList.style.display = "flex";
      el.btnCheckout.disabled = false;

      el.cartItemsList.innerHTML = "";
      items.forEach((row, index) => {
        const itemSubtotal = row.menuItem.price * row.quantity;
        const rowEl = document.createElement("div");
        rowEl.className = "cart-row";
        rowEl.innerHTML = `
          <div>
            <div class="cart-item-name">${row.menuItem.name}</div>
            <div class="cart-item-price">${formatMoney(row.menuItem.price)} each</div>
          </div>
          <div class="stepper">
            <button class="btn-dec" data-idx="${index}" aria-label="Decrease quantity">−</button>
            <span>${row.quantity}</span>
            <button class="btn-inc" data-idx="${index}" aria-label="Increase quantity">+</button>
          </div>
          <div class="cart-row-total">${formatMoney(itemSubtotal)}</div>
          <button class="cart-row-remove" data-idx="${index}" title="Remove item">✕</button>
        `;
        el.cartItemsList.appendChild(rowEl);
      });
    }

    const { subtotal, tax, grandTotal } = calculateTotals();
    el.summarySubtotal.textContent = formatMoney(subtotal);
    el.summaryTax.textContent = formatMoney(tax);
    el.summaryTotal.textContent = formatMoney(grandTotal);
    el.btnCheckoutAmount.textContent = `${formatMoney(grandTotal)} →`;

    el.orderLabel.textContent = `Order #${state.activeOrder.orderId}`;
    el.headerOrderId.textContent = state.activeOrder.orderId;
  }

  function renderCustomerInfo() {
    const cust = state.activeOrder.customer;
    el.selectedCustomerName.textContent = cust.name;
    el.selectedCustomerPhone.textContent = cust.phone ? cust.phone : "Tap to change customer";
    el.statCustomerName.textContent = cust.name;
  }

  function renderStatsAndHistory() {
    const completed = state.ordersHistory.filter((o) => o.status === "COMPLETED");
    const totalRev = completed.reduce((sum, o) => sum + o.total, 0);

    el.statRevenue.textContent = formatMoney(totalRev);
    el.statOrders.textContent = completed.length;
    el.historyCount.textContent = state.ordersHistory.length;

    if (state.ordersHistory.length === 0) {
      el.emptyHistoryView.style.display = "block";
      el.historyTableBody.innerHTML = "";
    } else {
      el.emptyHistoryView.style.display = "none";
      el.historyTableBody.innerHTML = state.ordersHistory
        .map(
          (o) => `
          <tr>
            <td><strong>#${o.orderId}</strong></td>
            <td>${o.timestamp || "-"}</td>
            <td>${o.customer ? o.customer.name : "Walk-in"}</td>
            <td><span class="badge">${o.diningMode === "takeaway" ? "Takeaway" : (o.tableNumber || "Dine-in")}</span></td>
            <td>${(o.items || []).map((i) => `${i.quantity}x ${i.menuItem ? i.menuItem.name : (i.name || "Item")}`).join(", ")}</td>
            <td><strong>${formatMoney(o.total)}</strong></td>
            <td><span class="badge">${(o.paymentMethod || "Cash").toUpperCase()}</span></td>
            <td><span class="badge ${o.status === "completed" || o.status === "COMPLETED" ? "badge-success" : "badge-pending"}">${(o.status || "COMPLETED").toUpperCase()}</span></td>
            <td><button class="secondary-button btn-view-receipt" data-order="${o.orderId}">View</button></td>
          </tr>
        `
        )
        .join("");
    }
  }

  function renderTables() {
    if (!el.tablesGrid) return;
    el.tablesGrid.innerHTML = state.tables
      .map(
        (t) => `
        <div class="table-card ${t.status === "occupied" ? "occupied" : "available"}">
          <div class="table-card-top">
            <h3>${t.tableId}</h3>
            <span class="badge ${t.status === "occupied" ? "badge-occupied" : "badge-available"}">${t.status.toUpperCase()}</span>
          </div>
          <div class="table-card-body">
            <span>Section: <strong>${t.section}</strong></span>
            <span>Capacity: <strong>${t.capacity} Guests</strong></span>
            ${t.currentOrderId ? `<span>Active Order: <strong>#${t.currentOrderId}</strong></span>` : `<span>Status: <strong>Ready for seating</strong></span>`}
          </div>
          <div>
            <button class="secondary-button btn-toggle-table" data-id="${t.tableId}" data-status="${t.status}">
              ${t.status === "occupied" ? "🟢 Mark Available" : "🔴 Seat Guests"}
            </button>
          </div>
        </div>
      `
      )
      .join("");
  }

  function renderMenuMgmt() {
    if (!el.menuMgmtTableBody) return;
    el.menuMgmtTableBody.innerHTML = state.menuItems
      .map(
        (item) => `
        <tr>
          <td><strong>#${item.id}</strong></td>
          <td><strong>${item.name}</strong></td>
          <td><span class="menu-card-badge">${item.category || "mains"}</span></td>
          <td><strong>${formatMoney(item.price)}</strong></td>
          <td>
            <button class="destructive-button btn-delete-dish" data-id="${item.id}" style="padding: 4px 10px; font-size: 11px;">
              🗑️ Delete
            </button>
          </td>
        </tr>
      `
      )
      .join("");
  }

  function renderReports() {
    const completed = state.ordersHistory.filter(
      (o) => (o.status || "").toLowerCase() === "completed"
    );
    const totalRev = completed.reduce((sum, o) => sum + (Number(o.total) || 0), 0);
    const aov = completed.length > 0 ? totalRev / completed.length : 0;

    if (el.reportTotalRev) el.reportTotalRev.textContent = formatMoney(totalRev);
    if (el.reportCompletedOrders) el.reportCompletedOrders.textContent = completed.length;
    if (el.reportAov) el.reportAov.textContent = formatMoney(aov);

    // Calculate bestsellers
    const counts = {};
    completed.forEach((o) => {
      (o.items || []).forEach((row) => {
        const name = (row.menuItem ? row.menuItem.name : row.name) || "Dish";
        const qty = Number(row.quantity) || 1;
        counts[name] = (counts[name] || 0) + qty;
      });
    });

    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    if (el.reportBestsellersList) {
      if (sorted.length === 0) {
        el.reportBestsellersList.innerHTML = `<p style="color:var(--muted); font-size:13px;">No completed sales records yet.</p>`;
      } else {
        el.reportBestsellersList.innerHTML = sorted
          .map(
            ([name, qty], idx) => `
            <div class="bestseller-row">
              <div>
                <span class="bestseller-rank">#${idx + 1}</span>
                <strong>${name}</strong>
              </div>
              <span class="badge badge-success">${qty} sold</span>
            </div>
          `
          )
          .join("");
      }
    }
  }

  async function syncFromBackend() {
    try {
      const resMenu = await fetch("/api/menu");
      if (resMenu.ok) {
        const data = await resMenu.json();
        if (Array.isArray(data) && data.length > 0) {
          state.menuItems = data;
          renderMenu();
          renderMenuMgmt();
        }
      }

      const resTables = await fetch("/api/tables");
      if (resTables.ok) {
        const data = await resTables.json();
        if (Array.isArray(data) && data.length > 0) {
          state.tables = data;
          renderTables();
        }
      }

      const resOrders = await fetch("/api/orders");
      if (resOrders.ok) {
        const data = await resOrders.json();
        if (Array.isArray(data) && data.length > 0) {
          state.ordersHistory = data.reverse();
          renderStatsAndHistory();
          renderReports();
        }
      }

      const statusDot = document.querySelector(".status-dot");
      const statusText = document.getElementById("backend-status");
      if (statusDot) statusDot.classList.add("online");
      if (statusText) statusText.textContent = "Online (API Connected)";
    } catch (err) {
      console.log("Operating in standalone offline mode");
    }
  }

  // --- Order Actions (State Transitions) ---

  function addItemToOrder(menuItem) {
    if (state.activeOrder.status !== "PENDING") {
      showToast("Order is already locked");
      return;
    }

    const existing = state.activeOrder.items.find((i) => i.menuItem.id === menuItem.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      state.activeOrder.items.push({ menuItem, quantity: 1 });
    }
    renderCart();
    showToast(`Added ${menuItem.name}`);
  }

  function updateItemQuantity(index, delta) {
    const row = state.activeOrder.items[index];
    if (!row) return;

    row.quantity += delta;
    if (row.quantity <= 0) {
      state.activeOrder.items.splice(index, 1);
    }
    renderCart();
  }

  function removeItemFromOrder(index) {
    state.activeOrder.items.splice(index, 1);
    renderCart();
  }

  function clearActiveOrder() {
    if (state.activeOrder.items.length === 0) return;
    state.activeOrder.items = [];
    renderCart();
    showToast("Cart cleared");
  }

  // --- Modal Logic ---

  function openModal(modalEl) {
    if (!el.modalBackdrop) el.modalBackdrop = document.getElementById("modal-backdrop");
    if (!el.modalBackdrop) return;

    el.modalBackdrop.hidden = false;
    el.modalBackdrop.style.display = "grid";
    [el.modalPayment, el.modalCustomer, el.modalReceipt, el.modalNewItem].forEach((m) => {
      if (m) m.style.display = "none";
    });
    if (modalEl) modalEl.style.display = "block";
  }

  function closeModal() {
    if (!el.modalBackdrop) el.modalBackdrop = document.getElementById("modal-backdrop");
    if (!el.modalBackdrop) return;

    el.modalBackdrop.hidden = true;
    el.modalBackdrop.style.display = "none";
    [el.modalPayment, el.modalCustomer, el.modalReceipt, el.modalNewItem].forEach((m) => {
      if (m) m.style.display = "none";
    });
  }

  function openPaymentModal() {
    const { grandTotal } = calculateTotals();
    if (state.activeOrder.items.length === 0) {
      showToast("Cannot checkout an empty order");
      return;
    }

    el.paymentDueAmount.textContent = formatMoney(grandTotal);
    el.cashReceivedInput.value = grandTotal.toFixed(2);
    updateCashChange();
    el.cashError.style.display = "none";
    el.cardError.style.display = "none";
    el.qrError.style.display = "none";

    // Auto-generate sample QR Txn ID
    el.qrTxnInput.value = `TXN-${Date.now().toString().slice(-6)}`;

    setPaymentMethod("cash");
    openModal(el.modalPayment);
    setTimeout(() => {
      el.cashReceivedInput.focus();
      el.cashReceivedInput.select();
    }, 50);
  }

  function setPaymentMethod(method) {
    state.paymentMethod = method;
    document.querySelectorAll(".payment-tab").forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.method === method);
    });

    document.getElementById("tab-cash").style.display = method === "cash" ? "block" : "none";
    document.getElementById("tab-card").style.display = method === "card" ? "block" : "none";
    document.getElementById("tab-qr").style.display = method === "qr" ? "block" : "none";

    if (method === "cash") {
      setTimeout(() => {
        el.cashReceivedInput.focus();
        el.cashReceivedInput.select();
      }, 50);
    } else if (method === "card") {
      setTimeout(() => el.cardNumberInput.focus(), 50);
    } else if (method === "qr") {
      setTimeout(() => el.qrTxnInput.focus(), 50);
    }
  }

  function updateCashChange() {
    const { grandTotal } = calculateTotals();
    const received = parseFloat(el.cashReceivedInput.value) || 0;
    const diff = received - grandTotal;
    if (diff >= 0) {
      el.cashChangeAmount.textContent = formatMoney(diff);
      el.cashError.style.display = "none";
    } else {
      el.cashChangeAmount.textContent = "฿0.00";
      el.cashError.style.display = "block";
    }
  }

  function processPaymentSubmission() {
    const { grandTotal, subtotal, tax } = calculateTotals();
    const method = state.paymentMethod;

    if (method === "cash") {
      const received = parseFloat(el.cashReceivedInput.value) || 0;
      if (received < grandTotal) {
        el.cashError.style.display = "block";
        return;
      }
      completeOrderFlow({
        method: "Cash",
        receivedAmount: received,
        change: received - grandTotal
      });
    } else if (method === "card") {
      const rawCard = el.cardNumberInput.value.replace(/[\s-]/g, "");
      if (rawCard.length !== 16 || !/^\d+$/.test(rawCard)) {
        el.cardError.style.display = "block";
        return;
      }
      completeOrderFlow({
        method: "Credit Card",
        maskedCard: `****-****-****-${rawCard.slice(-4)}`
      });
    } else if (method === "qr") {
      const txn = el.qrTxnInput.value.trim();
      if (!txn) {
        el.qrError.style.display = "block";
        return;
      }
      completeOrderFlow({
        method: "QR Code",
        transactionId: txn
      });
    }
  }

  function completeOrderFlow(paymentDetails) {
    const { subtotal, tax, grandTotal } = calculateTotals();
    const now = new Date();
    const timestampStr = now.toLocaleDateString() + " " + now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const tableInfo = state.activeOrder.diningMode === "dinein" ? `Table: ${state.activeOrder.tableNumber}` : "Takeaway";

    const finishedOrder = {
      orderId: state.activeOrder.orderId,
      customer: { ...state.activeOrder.customer },
      diningMode: state.activeOrder.diningMode,
      tableNumber: tableInfo,
      items: JSON.parse(JSON.stringify(state.activeOrder.items)),
      subtotal,
      tax,
      total: grandTotal,
      status: "COMPLETED",
      paymentMethod: paymentDetails.method,
      paymentDetails,
      timestamp: timestampStr
    };

    state.ordersHistory.unshift(finishedOrder);
    renderStatsAndHistory();
    renderReports();

    // Mark table as occupied in local table state if dine-in
    if (state.activeOrder.diningMode === "dinein") {
      const tbl = state.tables.find(t => t.tableId === state.activeOrder.tableNumber);
      if (tbl) {
        tbl.status = "occupied";
        tbl.currentOrderId = finishedOrder.orderId;
        renderTables();
      }
    }

    // Sync with backend API
    fetch("/api/orders/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customerName: finishedOrder.customer.name,
        customerPhone: finishedOrder.customer.phone,
        diningMode: finishedOrder.diningMode,
        tableNumber: state.activeOrder.tableNumber,
        items: finishedOrder.items.map((i) => ({ id: i.menuItem.id, quantity: i.quantity })),
        payment: {
          method: paymentDetails.method.toLowerCase(),
          receivedAmount: paymentDetails.receivedAmount,
          cardNumber: paymentDetails.maskedCard,
          transactionId: paymentDetails.transactionId
        }
      })
    }).catch(() => {});

    // Populate Receipt
    el.receiptOrderId.textContent = `#${finishedOrder.orderId}`;
    el.receiptCustomer.textContent = finishedOrder.customer.name;
    if (el.receiptDiningMode) el.receiptDiningMode.textContent = tableInfo;
    el.receiptTimestamp.textContent = timestampStr;
    el.receiptSubtotal.textContent = formatMoney(subtotal);
    el.receiptTax.textContent = formatMoney(tax);
    el.receiptTotal.textContent = formatMoney(grandTotal);
    el.receiptPaymentMethod.textContent = paymentDetails.method;

    if (paymentDetails.change !== undefined) {
      el.receiptChangeRow.style.display = "flex";
      el.receiptChange.textContent = formatMoney(paymentDetails.change);
    } else {
      el.receiptChangeRow.style.display = "none";
    }

    el.receiptItemsList.innerHTML = finishedOrder.items
      .map(
        (i) => `
        <div>
          <span>${i.quantity}x ${i.menuItem.name}</span>
          <span>${formatMoney(i.menuItem.price * i.quantity)}</span>
        </div>
      `
      )
      .join("");

    openModal(el.modalReceipt);
    showToast(`Order #${finishedOrder.orderId} completed successfully!`);
  }

  function startNextOrder() {
    state.orderSequence += 1;
    state.activeOrder = {
      orderId: state.orderSequence,
      customer: { name: "Walk-in Guest", phone: "" },
      diningMode: "dinein",
      tableNumber: el.selectTable ? el.selectTable.value : "T-01",
      items: [],
      status: "PENDING"
    };
    if (el.btnModeDinein) el.btnModeDinein.classList.add("active");
    if (el.btnModeTakeaway) el.btnModeTakeaway.classList.remove("active");
    if (el.tableSelectorRow) el.tableSelectorRow.style.display = "flex";
    renderCustomerInfo();
    renderCart();
    closeModal();
  }

  // --- Event Listeners Setup ---

  function setupEventListeners() {
    // Stepper and Remove clicks in cart
    el.cartItemsList.addEventListener("click", (e) => {
      const incBtn = e.target.closest(".btn-inc");
      const decBtn = e.target.closest(".btn-dec");
      const rmBtn = e.target.closest(".cart-row-remove");

      if (incBtn) updateItemQuantity(parseInt(incBtn.dataset.idx, 10), 1);
      if (decBtn) updateItemQuantity(parseInt(decBtn.dataset.idx, 10), -1);
      if (rmBtn) removeItemFromOrder(parseInt(rmBtn.dataset.idx, 10));
    });

    // Dining Mode Toggles
    if (el.btnModeDinein && el.btnModeTakeaway) {
      el.btnModeDinein.addEventListener("click", () => {
        el.btnModeDinein.classList.add("active");
        el.btnModeTakeaway.classList.remove("active");
        el.tableSelectorRow.style.display = "flex";
        state.activeOrder.diningMode = "dinein";
      });

      el.btnModeTakeaway.addEventListener("click", () => {
        el.btnModeTakeaway.classList.add("active");
        el.btnModeDinein.classList.remove("active");
        el.tableSelectorRow.style.display = "none";
        state.activeOrder.diningMode = "takeaway";
      });
    }

    if (el.selectTable) {
      el.selectTable.addEventListener("change", (e) => {
        state.activeOrder.tableNumber = e.target.value;
      });
    }

    // Category pills
    if (el.categoryPills) {
      el.categoryPills.addEventListener("click", (e) => {
        const pill = e.target && e.target.closest ? e.target.closest(".category-pill") : null;
        if (!pill) return;
        document.querySelectorAll(".category-pill").forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        state.selectedCategory = (pill.dataset && pill.dataset.cat) ? pill.dataset.cat.toLowerCase() : "all";
        renderMenu();
      });
    }

    // Search input & Clear button
    if (el.searchInput) {
      el.searchInput.addEventListener("input", (e) => {
        const val = e && e.target ? String(e.target.value || "") : "";
        state.searchQuery = val.trim();
        if (el.btnClearSearch) {
          el.btnClearSearch.style.display = state.searchQuery ? "block" : "none";
        }
        renderMenu();
      });
    }

    if (el.btnClearSearch) {
      el.btnClearSearch.addEventListener("click", () => {
        if (el.searchInput) el.searchInput.value = "";
        state.searchQuery = "";
        el.btnClearSearch.style.display = "none";
        renderMenu();
        if (el.searchInput) el.searchInput.focus();
      });
    }

    // Cashier Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      // '/' to focus search when not in an input
      if (
        e.key === "/" &&
        document.activeElement !== el.searchInput &&
        document.activeElement.tagName !== "INPUT" &&
        el.modalBackdrop.hidden
      ) {
        e.preventDefault();
        el.searchInput.focus();
        el.searchInput.select();
      } else if (e.key === "Escape") {
        closeModal();
      } else if (e.key === "Enter" && !el.modalBackdrop.hidden) {
        if (el.modalPayment && el.modalPayment.style.display === "block") {
          e.preventDefault();
          processPaymentSubmission();
        }
      }
    });

    // Clear order
    el.btnClearOrder.addEventListener("click", clearActiveOrder);

    // Checkout button
    el.btnCheckout.addEventListener("click", openPaymentModal);

    // Payment Tabs
    document.querySelectorAll(".payment-tab").forEach((tab) => {
      tab.addEventListener("click", () => setPaymentMethod(tab.dataset.method));
    });

    // Cash quick buttons
    document.querySelectorAll(".quick-cash").forEach((btn) => {
      btn.addEventListener("click", () => {
        const val = btn.dataset.val;
        const { grandTotal } = calculateTotals();
        if (val === "exact") {
          el.cashReceivedInput.value = grandTotal.toFixed(2);
        } else {
          el.cashReceivedInput.value = parseFloat(val).toFixed(2);
        }
        updateCashChange();
      });
    });

    el.cashReceivedInput.addEventListener("input", updateCashChange);

    // Card Input Formatter
    el.cardNumberInput.addEventListener("input", (e) => {
      let val = e.target.value.replace(/\D/g, "").slice(0, 16);
      val = val.replace(/(\d{4})(?=\d)/g, "$1 ");
      e.target.value = val;
    });

    // Confirm Payment
    el.btnConfirmPayment.addEventListener("click", processPaymentSubmission);

    // Close modals
    document.querySelectorAll("[data-close='true']").forEach((b) => {
      b.addEventListener("click", closeModal);
    });

    el.modalBackdrop.addEventListener("click", (e) => {
      if (e.target === el.modalBackdrop) closeModal();
    });

    // Start next order from receipt
    document.getElementById("btn-new-order").addEventListener("click", startNextOrder);
    document.getElementById("btn-print-receipt").addEventListener("click", () => {
      window.print();
    });

    // Customer Selector Modal
    document.getElementById("btn-select-customer").addEventListener("click", () => {
      openModal(el.modalCustomer);
    });

    document.querySelectorAll(".customer-preset-card").forEach((card) => {
      card.addEventListener("click", () => {
        document.querySelectorAll(".customer-preset-card").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        document.getElementById("custom-customer-name").value = card.dataset.name;
        document.getElementById("custom-customer-phone").value = card.dataset.phone;
      });
    });

    document.getElementById("btn-save-customer").addEventListener("click", () => {
      const name = document.getElementById("custom-customer-name").value.trim() || "Walk-in Guest";
      const phone = document.getElementById("custom-customer-phone").value.trim();
      state.activeOrder.customer = { name, phone };
      renderCustomerInfo();
      closeModal();
      showToast(`Customer set to ${name}`);
    });

    // Add New Menu Item Modal
    document.getElementById("btn-add-custom-item").addEventListener("click", () => {
      openModal(el.modalNewItem);
    });

    document.getElementById("btn-save-new-item").addEventListener("click", () => {
      const name = document.getElementById("new-item-name").value.trim();
      const price = parseFloat(document.getElementById("new-item-price").value);
      const category = document.getElementById("new-item-category").value;

      if (!name || isNaN(price) || price <= 0) {
        showToast("Please enter a valid item name and positive price");
        return;
      }

      const newItem = {
        id: state.menuItems.length + 1,
        name,
        price,
        category,
        icon: category === "drinks" ? "🥤" : category === "desserts" ? "🍨" : "🍲"
      };

      state.menuItems.push(newItem);
      renderMenu();
      closeModal();
      showToast(`Added "${name}" to menu catalog!`);

      // Reset form
      document.getElementById("new-item-name").value = "";
      document.getElementById("new-item-price").value = "";
    });

    // Navigation Views Mapping
    const views = {
      pos: { el: el.viewPos, title: "Order Terminal", display: "grid" },
      history: { el: el.viewHistory, title: "Order History & Audit", display: "block" },
      tables: { el: el.viewTables, title: "Restaurant Table Map", display: "block", onOpen: renderTables },
      "menu-mgmt": { el: el.viewMenuMgmt, title: "Menu Catalog Manager", display: "block", onOpen: renderMenuMgmt },
      reports: { el: el.viewReports, title: "Sales Analytics & Reports", display: "block", onOpen: renderReports }
    };

    function switchView(targetView) {
      document.querySelectorAll(".nav-link").forEach((l) => {
        l.classList.toggle("active", l.dataset.view === targetView);
      });

      Object.entries(views).forEach(([key, config]) => {
        if (!config.el) return;
        if (key === targetView) {
          config.el.style.display = config.display;
          const pageTitle = document.getElementById("page-title");
          if (pageTitle) pageTitle.textContent = config.title;
          if (config.onOpen) config.onOpen();
        } else {
          config.el.style.display = "none";
        }
      });
    }

    document.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => switchView(link.dataset.view));
    });

    document.querySelectorAll(".btn-go-pos").forEach((btn) => {
      btn.addEventListener("click", () => switchView("pos"));
    });

    const btnViewHistory = document.getElementById("btn-view-history");
    if (btnViewHistory) {
      btnViewHistory.addEventListener("click", () => switchView("history"));
    }

    // Table Status Toggle Handler
    if (el.tablesGrid) {
      el.tablesGrid.addEventListener("click", async (e) => {
        const btn = e.target.closest(".btn-toggle-table");
        if (!btn) return;
        const tableId = btn.dataset.id;
        const currStatus = btn.dataset.status;
        const newStatus = currStatus === "occupied" ? "available" : "occupied";

        const tbl = state.tables.find((t) => t.tableId === tableId);
        if (tbl) {
          tbl.status = newStatus;
          if (newStatus === "available") tbl.currentOrderId = null;
          renderTables();
        }

        try {
          await fetch("/api/tables/status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tableId, status: newStatus })
          });
          showToast(`Table ${tableId} is now ${newStatus.toUpperCase()}`);
        } catch (err) {}
      });
    }

    // Menu Management Delete Handler
    if (el.menuMgmtTableBody) {
      el.menuMgmtTableBody.addEventListener("click", async (e) => {
        const btn = e.target.closest(".btn-delete-dish");
        if (!btn) return;
        const dishId = parseInt(btn.dataset.id, 10);
        state.menuItems = state.menuItems.filter((m) => m.id !== dishId);
        renderMenu();
        renderMenuMgmt();
        showToast("Dish removed from catalog");
        try {
          await fetch(`/api/menu/${dishId}`, { method: "DELETE" });
        } catch (err) {}
      });
    }

    const btnOpenAddMenu = document.getElementById("btn-open-add-menu-modal");
    if (btnOpenAddMenu) {
      btnOpenAddMenu.addEventListener("click", () => openModal(el.modalNewItem));
    }

    // Receipt click in history
    el.historyTableBody.addEventListener("click", (e) => {
      const btn = e.target.closest(".btn-view-receipt");
      if (!btn) return;
      const orderId = parseInt(btn.dataset.order, 10);
      const found = state.ordersHistory.find((o) => o.orderId === orderId);
      if (found) {
        el.receiptOrderId.textContent = `#${found.orderId}`;
        el.receiptCustomer.textContent = found.customer ? found.customer.name : "Walk-in";
        if (el.receiptDiningMode) el.receiptDiningMode.textContent = found.tableNumber || "Dine-in";
        el.receiptTimestamp.textContent = found.timestamp || "";
        el.receiptSubtotal.textContent = formatMoney(found.subtotal);
        el.receiptTax.textContent = formatMoney(found.tax);
        el.receiptTotal.textContent = formatMoney(found.total);
        el.receiptPaymentMethod.textContent = found.paymentMethod || "Cash";
        el.receiptItemsList.innerHTML = (found.items || [])
          .map(
            (i) => `
            <div>
              <span>${i.quantity}x ${i.menuItem ? i.menuItem.name : (i.name || "Dish")}</span>
              <span>${formatMoney((i.menuItem ? i.menuItem.price : i.price) * i.quantity)}</span>
            </div>
          `
          )
          .join("");
        openModal(el.modalReceipt);
      }
    });
  }

  // --- Initialization ---
  async function init() {
    const today = new Date();
    if (el.currentDate) {
      el.currentDate.textContent = today.toLocaleDateString(undefined, {
        weekday: "long",
        month: "long",
        day: "numeric"
      });
    }

    closeModal();
    renderMenu();
    renderCustomerInfo();
    renderCart();
    renderStatsAndHistory();
    renderTables();
    renderMenuMgmt();
    renderReports();
    setupEventListeners();
    await syncFromBackend();
  }

  // Run on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
