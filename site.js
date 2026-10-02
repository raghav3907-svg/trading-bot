const menuButton = document.getElementById('menu-button');
const siteNav = document.querySelector('.site-nav');
const toast = document.getElementById('toast');

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('visible');
  window.setTimeout(() => toast.classList.remove('visible'), 3600);
}

if (menuButton && siteNav) {
  menuButton.addEventListener('click', () => {
    const isOpen = siteNav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
  });
}

document.querySelectorAll('.site-nav a').forEach((link) => {
  link.addEventListener('click', () => siteNav.classList.remove('open'));
});

const orderForm = document.getElementById('order-form');
const orderType = document.getElementById('order-type');
const priceLabel = document.getElementById('price-label');

if (orderForm && orderType && priceLabel) {
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
  updatePriceField();
}

const refreshButton = document.getElementById('refresh-button');
if (refreshButton) {
  refreshButton.addEventListener('click', (event) => {
    event.currentTarget.textContent = 'Updated just now ✓';
    showToast('Demo dashboard refreshed.');
  });
}

const chart = document.getElementById('market-chart');
if (chart) {
  const marketData = {
    BTCUSDT: { title: 'BTC / USDT', category: 'CRYPTO / TESTNET DATA', price: '$60,840.00', change: '+4.82%', values: [38, 52, 44, 64, 57, 73, 68, 88, 82, 96] },
    ETHUSDT: { title: 'ETH / USDT', category: 'CRYPTO / TESTNET DATA', price: '$3,242.50', change: '+2.36%', values: [42, 48, 41, 60, 56, 65, 63, 76, 71, 83] },
    SOLUSDT: { title: 'SOL / USDT', category: 'CRYPTO / TESTNET DATA', price: '$142.50', change: '+8.14%', values: [30, 44, 39, 57, 52, 69, 61, 84, 78, 98] },
    SENSEX: { title: 'SENSEX', category: 'INDIA / INDEX DATA', price: '81,224.75', change: '+0.64%', values: [62, 58, 65, 61, 68, 71, 69, 78, 74, 84] },
    NIFTY50: { title: 'NIFTY 50', category: 'INDIA / INDEX DATA', price: '24,836.10', change: '+0.71%', values: [55, 60, 57, 65, 63, 72, 68, 77, 75, 88] }
  };
  const title = document.getElementById('chart-title');
  const category = document.getElementById('chart-category');
  const price = document.getElementById('chart-price');
  const change = document.getElementById('chart-change');
  const marketSelect = document.getElementById('market-select');
  const currencySelect = document.getElementById('currency-select');
  const chartType = document.getElementById('chart-type');
  const currencyRates = { USD: 1, INR: 83.2, EUR: .92 };
  const drawChart = () => {
    const asset = marketData[marketSelect.value];
    const rate = currencyRates[currencySelect.value];
    const suffix = currencySelect.value === 'USD' ? '$' : currencySelect.value === 'INR' ? '₹' : '€';
    const rawPrice = Number(asset.price.replace(/[$,]/g, '')) * rate;
    title.textContent = asset.title;
    category.textContent = asset.category;
    price.textContent = `${suffix}${rawPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    change.textContent = `${asset.change} this month`;
    const points = asset.values.map((value, index) => `${index * 100},${300 - value * 2.5}`).join(' ');
    const grid = '<path class="chart-grid" d="M0 75H900M0 150H900M0 225H900M0 300H900"/>';
    let graphic = `<defs><linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d95d39" stop-opacity=".22"/><stop offset="1" stop-color="#d95d39" stop-opacity="0"/></linearGradient></defs>${grid}<polygon class="chart-area" points="${points} 900,330 0,330"/><polyline class="chart-line" points="${points}"/>`;
    if (chartType.value === 'candle') {
      const candles = asset.values.map((value, index) => {
        const open = value - (index % 3 === 0 ? 5 : -4);
        const close = value;
        const high = Math.max(open, close) + 10;
        const low = Math.min(open, close) - 8;
        const color = close >= open ? 'candle-up' : 'candle-down';
        const x = index * 100 + 43;
        const bodyY = 300 - Math.max(open, close) * 2.5;
        const bodyHeight = Math.max(8, Math.abs(close - open) * 2.5);
        return `<line class="${color}" x1="${x + 7}" y1="${300 - high * 2.5}" x2="${x + 7}" y2="${300 - low * 2.5}"/><rect class="${color}" x="${x}" y="${bodyY}" width="14" height="${bodyHeight}"/>`;
      }).join('');
      graphic = `${grid}<g class="candles">${candles}</g>`;
    }
    if (chartType.value === 'bars') {
      const bars = asset.values.map((value, index) => `<rect class="volume-bar" x="${index * 100 + 25}" y="${330 - value * 2.2}" width="50" height="${value * 2.2}" rx="2"/>`).join('');
      graphic = `${grid}<g class="volume-bars">${bars}</g>`;
    }
    chart.innerHTML = graphic;
  };
  marketSelect.addEventListener('change', drawChart);
  currencySelect.addEventListener('change', drawChart);
  chartType.addEventListener('change', drawChart);
  document.querySelectorAll('.period-tab').forEach((tab) => tab.addEventListener('click', () => {
    document.querySelectorAll('.period-tab').forEach((item) => item.classList.remove('active'));
    tab.classList.add('active');
    drawChart();
    showToast(`${tab.dataset.period} chart view selected.`);
  }));
  drawChart();
}