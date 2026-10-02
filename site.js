const menuButton = document.getElementById('menu-button');
const siteNav = document.querySelector('.site-nav');
const orderForm = document.getElementById('order-form');
const orderType = document.getElementById('order-type');
const priceLabel = document.getElementById('price-label');
const toast = document.getElementById('toast');

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('visible');
  window.setTimeout(() => toast.classList.remove('visible'), 3600);
}

menuButton.addEventListener('click', () => {
  const isOpen = siteNav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
});

document.querySelectorAll('.site-nav a').forEach((link) => {
  link.addEventListener('click', () => siteNav.classList.remove('open'));
});

function updatePriceField() {
  const needsPrice = orderType.value !== 'MARKET';
  priceLabel.hidden = !needsPrice;
  priceLabel.querySelector('input').required = needsPrice;
}

orderType.addEventListener('change', updatePriceField);
orderForm.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!orderForm.reportValidity()) return;
  showToast('Demo only: connect the Flask backend to place live testnet orders.');
});

document.getElementById('refresh-button').addEventListener('click', (event) => {
  event.currentTarget.textContent = 'Updated just now ✓';
  showToast('Demo dashboard refreshed.');
});

updatePriceField();