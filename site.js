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
  const chartTooltip = document.getElementById('chart-tooltip');
  const currencyRates = { USD: 1, INR: 83.2, EUR: .92 };
  const expandSeries = (seed) => Array.from({ length: 30 }, (_, index) => {
    const position = index / 29 * (seed.length - 1);
    const lower = Math.floor(position);
    const upper = Math.min(seed.length - 1, lower + 1);
    const blend = position - lower;
    const drift = ((index * 17) % 7) - 3;
    return seed[lower] + (seed[upper] - seed[lower]) * blend + drift;
  });
  const drawChart = () => {
    const asset = marketData[marketSelect.value];
    const values = expandSeries(asset.values);
    const rate = currencyRates[currencySelect.value];
    const suffix = currencySelect.value === 'USD' ? '$' : currencySelect.value === 'INR' ? '₹' : '€';
    const rawPrice = Number(asset.price.replace(/[$,]/g, '')) * rate;
    title.textContent = asset.title;
    category.textContent = asset.category;
    price.textContent = `${suffix}${rawPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    change.textContent = `${asset.change} this month`;
    const xFor = (index) => 22 + index * (856 / (values.length - 1));
    const yFor = (value) => 245 - value * 2.05;
    const points = values.map((value, index) => `${xFor(index)},${yFor(value)}`).join(' ');
    const grid = '<path class="chart-grid" d="M0 40H900M0 95H900M0 150H900M0 205H900M0 260H900M0 315H900M22 20V315M236 20V315M450 20V315M664 20V315M878 20V315"/>';
    const axes = '<text class="chart-axis" x="8" y="44">100</text><text class="chart-axis" x="8" y="154">50</text><text class="chart-axis" x="8" y="264">0</text><text class="chart-axis" x="810" y="345">VOLUME</text>';
    let graphic = `<defs><linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d95d39" stop-opacity=".2"/><stop offset="1" stop-color="#d95d39" stop-opacity="0"/></linearGradient></defs>${grid}${axes}<polygon class="chart-area" points="${points} 878,315 22,315"/><polyline class="chart-line" points="${points}"/>`;
    if (chartType.value === 'candle') {
      const candles = values.map((value, index) => {
        const open = value - (index % 3 === 0 ? 5 : -4);
        const close = value;
        const high = Math.max(open, close) + 7 + (index % 4);
        const low = Math.min(open, close) - 6 - (index % 3);
        const color = close >= open ? 'candle-up' : 'candle-down';
        const x = xFor(index) - 6;
        const bodyY = yFor(Math.max(open, close));
        const bodyHeight = Math.max(5, Math.abs(close - open) * 2.05);
        return `<line class="${color}" x1="${x + 6}" y1="${yFor(high)}" x2="${x + 6}" y2="${yFor(low)}"/><rect class="${color}" x="${x}" y="${bodyY}" width="12" height="${bodyHeight}" rx="1"/>`;
      }).join('');
      const volume = values.map((value, index) => `<rect class="volume-bar ${index % 2 ? 'bar-down' : 'bar-up'}" x="${xFor(index) - 5}" y="${315 - (value % 23) * 1.8}" width="10" height="${(value % 23) * 1.8}" rx="1"/>`).join('');
      graphic = `${grid}${axes}<g class="candles">${candles}</g><g class="volume-bars">${volume}</g>`;
    }
    if (chartType.value === 'bars') {
      const bars = values.map((value, index) => `<rect class="volume-bar ${index % 2 ? 'bar-down' : 'bar-up'}" x="${xFor(index) - 9}" y="${315 - value * 2.4}" width="18" height="${value * 2.4}" rx="2"/>`).join('');
      graphic = `${grid}${axes}<g class="volume-bars">${bars}</g>`;
    }
    chart.innerHTML = graphic;
    chart.onpointermove = (event) => {
      if (!chartTooltip) return;
      const bounds = chart.getBoundingClientRect();
      const index = Math.max(0, Math.min(values.length - 1, Math.round((event.clientX - bounds.left) / bounds.width * (values.length - 1))));
      chartTooltip.textContent = `O ${Math.round(values[index] - 4)}  H ${Math.round(values[index] + 8)}  L ${Math.round(values[index] - 9)}  C ${Math.round(values[index])}`;
      chartTooltip.style.left = `${Math.min(78, Math.max(2, (index / (values.length - 1)) * 86))}%`;
      chartTooltip.classList.add('is-visible');
    };
    chart.onpointerleave = () => chartTooltip && chartTooltip.classList.remove('is-visible');
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