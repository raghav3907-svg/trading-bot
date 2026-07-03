# Trading Bot — Binance Futures Testnet (USDT-M)

A simplified CLI trading bot that places Market, Limit, and Stop-Limit
orders on Binance Futures Testnet, with structured code, input
validation, and logging.

## Features

- **Order types:** MARKET, LIMIT, and STOP_LIMIT (bonus)
- **Both sides:** BUY and SELL
- **CLI input** via `argparse`, with validation before any API call
- **Structured layout:** separate API client layer (`bot/client.py`)
  and CLI/command layer (`cli.py`)
- **Logging:** every request, response, and error is logged to
  `logs/trading_bot.log` (rotating file handler) and summarized on
  the console

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client wrapper (signing, requests)
│   ├── orders.py          # order placement logic / summaries
│   ├── validators.py      # input validation
│   └── logging_config.py  # logging setup
├── cli.py                 # CLI entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── logs/                  # log output (created automatically)
```

## Setup

1. **Clone the repo and install dependencies:**

   ```bash
   git clone <your-repo-url>
   cd trading_bot
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create a Binance Futures Testnet account:**
   - Go to https://testnet.binancefuture.com
   - Log in with GitHub
   - Generate an HMAC_SHA256 API key + secret

3. **Configure credentials:**

   ```bash
   cp .env.example .env
   # then edit .env and paste your key/secret
   ```

   `.env` is git-ignored — never commit real API keys.

## How to Run

**Check your connection/API keys first:**

```bash
python cli.py --check-connection
```

**Place a Market order:**

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Place a Limit order:**

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

**Place a Stop-Limit order (bonus order type):**

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
  --quantity 0.01 --price 61000 --stop-price 60800
```

Each run prints:
- an order request summary
- the order response (orderId, status, executedQty, avgPrice)
- a clear success/failure message

Full request/response/error details are written to `logs/trading_bot.log`.

## Assumptions

- Quantities and prices used in examples are small/arbitrary testnet
  values — adjust to the symbol's actual minimum notional/lot size
  (testnet enforces the same filters as production Binance Futures).
- `timeInForce` defaults to `GTC` for LIMIT and STOP_LIMIT orders.
- STOP_LIMIT is implemented as Binance's `STOP` order type (a
  stop-limit order that triggers a limit order once `stopPrice` is hit).
- Error handling covers three categories: input validation errors
  (before any network call), Binance API errors (non-200 responses),
  and network errors (timeouts/connection failures).

## Testing Notes

To generate the two required log files (one MARKET, one LIMIT order),
run the two example commands above against your funded testnet
account, then include the resulting `logs/trading_bot.log` (or copies
of the relevant lines) in your submission.
