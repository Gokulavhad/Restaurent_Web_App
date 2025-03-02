let cart = [];

function addToCart(id, name, price) {
    const existingItem = cart.find(item => item.id === id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: id,
            name: name,
            price: price,
            quantity: 1
        });
    }
    
    updateCartCount();
    showNotification(`Added ${name} to cart`);
}

function updateCartCount() {
    const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
    document.getElementById('cart-count').textContent = cartCount;
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 2000);
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    
    cartItems.innerHTML = '';
    let total = 0;
    
    cart.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <span>${item.name} x ${item.quantity}</span>
            <span>$${(item.price * item.quantity).toFixed(2)}</span>
            <button onclick="removeFromCart(${item.id})">Remove</button>
        `;
        cartItems.appendChild(itemElement);
        total += item.price * item.quantity;
    });
    
    cartTotal.textContent = `Total: $${total.toFixed(2)}`;
}

function removeFromCart(id) {
    const index = cart.findIndex(item => item.id === id);
    if (index !== -1) {
        cart.splice(index, 1);
        updateCartCount();
        updateCartDisplay();
    }
}

// Cart Modal
const cartModal = document.getElementById('cart-modal');
const cartLink = document.querySelector('a[href="#cart"]');
const closeCart = document.getElementById('close-cart');
const placeOrder = document.getElementById('place-order');

cartLink.addEventListener('click', (e) => {
    e.preventDefault();
    cartModal.style.display = 'block';
    updateCartDisplay();
});

closeCart.addEventListener('click', () => {
    cartModal.style.display = 'none';
});

placeOrder.addEventListener('click', async () => {
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }
    
    try {
        const response = await fetch('/place-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: cart,
                total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
            })
        });
        
        const data = await response.json();
        alert(data.message);
        cart = [];
        updateCartCount();
        cartModal.style.display = 'none';
    } catch (error) {
        alert('Error placing order. Please try again.');
    }
});
