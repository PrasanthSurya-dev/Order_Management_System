// ====================
// Customer data (from meta)
// ====================
const customer = {
  name: document.querySelector("meta[name='customer_name']")?.content || "Guest",
  address: document.querySelector("meta[name='customer_address']")?.content || "N/A",
  contact: document.querySelector("meta[name='customer_contact']")?.content || "N/A"
};

let products = [];
let cart = {};
let orders = [];

// ====================
// Load products & orders from server
// ====================
document.addEventListener("DOMContentLoaded", function() {
  loadProducts();
  loadOrders();

  const productsSection = document.getElementById("productsSection");
  const cartCount = document.getElementById("cartCount");
  const cartOverlay = document.getElementById("cartOverlay");
  const cartItemsDiv = document.getElementById("cartItems");
  const cartTotalDiv = document.getElementById("cartTotal");
  const placeOrderSection = document.getElementById("placeOrderSection");
  const orderHistorySection = document.getElementById("orderHistorySection");
  const orderHistoryList = document.getElementById("orderHistoryList");
  const homeBtn = document.getElementById("homeBtn");
  const ordersBtn = document.getElementById("ordersBtn");
  const closeCartBtn = document.getElementById("closeCart");

  updateCartCount();

  document.querySelector(".cartIcon").onclick = () => {
    showCart();
    cartOverlay.classList.remove("hidden");
  };

  closeCartBtn.onclick = () => cartOverlay.classList.add("hidden");

  homeBtn.onclick = () => {
    orderHistorySection.classList.add("hidden");
    productsSection.classList.remove("hidden");
    homeBtn.classList.add("active");
    ordersBtn.classList.remove("active");
  };
  ordersBtn.onclick = () => {
    orderHistorySection.classList.remove("hidden");
    productsSection.classList.add("hidden");
    homeBtn.classList.remove("active");
    ordersBtn.classList.add("active");
  };

  document.getElementById("logoutBtn")?.addEventListener("click", () => {
    window.location.href = "/logout";
  });
});

// ====================
// Load products from server
// ====================
function loadProducts() {
  fetch('/get_products')
    .then(res => res.json())
    .then(data => {
      products = data;
      renderProducts();
    });
}

// ====================
// Load orders from server
// ====================
function loadOrders() {
  fetch('/get_orders')
    .then(res => res.json())
    .then(data => {
      orders = data;
      renderOrders();
    });
}

// ====================
// Render products
// ====================

function renderProducts() {
  const productsSection = document.getElementById("productsSection");
  productsSection.innerHTML = "";
  let sorted = products.slice().sort((a,b) => (b.stock === 0) - (a.stock === 0));

  sorted.forEach(prod => {
    const div = document.createElement("div");
    div.className = "product-card " + (prod.stock === 0 ? "out-of-stock" : "");

    if (cart[prod.id]) {
      div.innerHTML = `
        <img src="${prod.image_url}" alt="${prod.name}">
        <h4>${prod.name}</h4>
        <p>₹${prod.price}</p>
        <p>Stock: ${prod.stock}</p>
        <div class="quantity">
          <button onclick="changeQty(${prod.id}, -1)">-</button>
          ${cart[prod.id]}
          <button onclick="changeQty(${prod.id}, 1)">+</button>
        </div>
      `;
    } else {
      div.innerHTML = `
        <img src="${prod.image_url}" alt="${prod.name}"> 
        <h4>${prod.name}</h4>
        <p>₹${prod.price}</p>
        <p>${prod.stock > 0 ? `Stock: ${prod.stock}` : "Out of Stock"}</p>
        ${prod.stock > 0 ? `<button onclick="addToCart(${prod.id})">Add to Cart</button>` : ""}
      `;
    }
    productsSection.appendChild(div);
  });
}

// ====================
// Cart functions
// ====================
function addToCart(id) {
  let prod = products.find(p => p.id === id);
  if (!prod || prod.stock <= 0) return;

  if (!cart[id]) cart[id] = 1;
  else if (cart[id] < 5 && cart[id] < prod.stock) cart[id]++;

  renderProducts();
  updateCartCount();
}

function changeQty(id, diff) {
  let prod = products.find(p => p.id === id);
  if (!prod) return;

  cart[id] = (cart[id] || 0) + diff;
  if (cart[id] <= 0) delete cart[id];
  else if (cart[id] > 5) cart[id] = 5;
  else if (cart[id] > prod.stock) cart[id] = prod.stock;

  renderProducts();
  updateCartCount();
  showCart();
}

function updateCartCount() {
  const cartCount = document.getElementById("cartCount");
  let totalQty = Object.values(cart).reduce((a,b) => a+b, 0);
  cartCount.textContent = totalQty;
}

// ====================
// Cart overlay
// ====================
function showCart() {
  const cartItemsDiv = document.getElementById("cartItems");
  const cartTotalDiv = document.getElementById("cartTotal");
  const placeOrderSection = document.getElementById("placeOrderSection");

  cartItemsDiv.innerHTML = "";
  let total = 0;
  Object.keys(cart).forEach(id => {
    let prod = products.find(p => p.id == id);
    let qty = cart[id];
    let line = document.createElement("div");
    line.className = "cartItem";
    line.innerHTML = `
      <span>${prod.name}</span>
      <div class="quantity">
        <button onclick="changeQty(${id}, -1)">-</button>
        ${qty}
        <button onclick="changeQty(${id}, 1)">+</button>
      </div>
      <span>₹${prod.price * qty}</span>
    `;
    cartItemsDiv.appendChild(line);
    total += prod.price * qty;
  });

  cartTotalDiv.textContent = "Total: ₹" + total;
  showPlaceOrderOptions(total);
}

function showPlaceOrderOptions(total) {
  const placeOrderSection = document.getElementById("placeOrderSection");
  if (total === 0) {
    placeOrderSection.innerHTML = "<p>Cart is empty.</p>";
    return;
  }
  placeOrderSection.innerHTML = `
    <button onclick="placeCOD(${total})">Cash on Delivery</button>
    <button onclick="selectOnline(${total})">Online Payment</button>
  `;
}

// ====================
// Place order
// ====================
function placeCOD(total) {
  const placeOrderSection = document.getElementById("placeOrderSection");
  placeOrderSection.innerHTML = `
    <p>Delivery to:</p>
    <p>${customer.name}, ${customer.address}, ${customer.contact}</p>
    <p>Estimated delivery in 5-7 days.</p>
    <button onclick="confirmOrder('Cash on Delivery', ${total})">Confirm Order</button>
  `;
}

function selectOnline(total) {
  const placeOrderSection = document.getElementById("placeOrderSection");
  placeOrderSection.innerHTML = `
    <p>Select Payment:</p>
    <button onclick="finalOnline('UPI', ${total})">UPI</button>
    <button onclick="finalOnline('Debit Card', ${total})">Debit Card</button>
    <button onclick="finalOnline('Credit Card', ${total})">Credit Card</button>
  `;
}

function finalOnline(method, total) {
  const placeOrderSection = document.getElementById("placeOrderSection");
  placeOrderSection.innerHTML = `
    <p>Payment mode: ${method}</p>
    <p>Delivery to: ${customer.name}, ${customer.address}, ${customer.contact}</p>
    <p>Estimated delivery in 5-7 days.</p>
    <button onclick="confirmOrder('${method}', ${total})">Confirm Order</button>
  `;
}

function confirmOrder(method, total) {
  fetch('/place_order', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cart, total, payment: method})
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      alert("Order placed!");
      cart = {};
      loadProducts();
      loadOrders();
      updateCartCount();
      document.getElementById("cartOverlay").classList.add("hidden");
    }
  });
}

// ====================
// Orders
// ====================
function renderOrders() {
    const orderHistoryList = document.getElementById("orderHistoryList");
    orderHistoryList.innerHTML = "";

    if (!orders || orders.length === 0) {
        orderHistoryList.innerHTML = "<p>You have no orders yet.</p>";
        return;
    }

    orders.forEach(order => {
        let div = document.createElement("div");
        div.className = "order-history-box";
        
        let contentWrapper = document.createElement("div");
        contentWrapper.className = "order-content-wrapper";

        let detailsDiv = document.createElement("div");
        
        let deliveryDisplayDate = '';
        if (order.status !== 'Cancelled') {
            deliveryDisplayDate = order.actual_delivery ? `| Delivered on: ${order.actual_delivery}` : `| Est. Delivery: ${order.delivery}`;
        }
        
        let detailsHtml = `
          <h4>Order #${order.id}</h4>
          <p>Payment: ${order.payment}</p>
          <p>Status: ${order.status}</p>
          <hr>
          <p>Items: ${order.items_text}</p>
          <p>Total: ₹${order.total} ${deliveryDisplayDate}</p>
        `;

        if (order.status === 'Cancelled' && order.cancellation_refund) {
            detailsHtml += `<p class="refund-status">${order.cancellation_refund}</p>`;
        }
        
        detailsDiv.innerHTML = detailsHtml;
        
        contentWrapper.appendChild(detailsDiv);

        if (order.status !== 'Delivered' && order.status !== 'Cancelled') {
            const cancelForm = document.createElement('form');
            cancelForm.action = `/confirm_cancel/${order.id}`;
            cancelForm.method = 'GET';
            
            const cancelButton = document.createElement('button');
            cancelButton.type = 'submit';
            cancelButton.className = 'btn btn-cancel-order';
            cancelButton.textContent = 'Cancel';
            
            cancelForm.appendChild(cancelButton);
            contentWrapper.appendChild(cancelForm);
        }
        
        div.appendChild(contentWrapper);
        orderHistoryList.appendChild(div);
    });
}