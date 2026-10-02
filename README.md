# Trading Bot Dashboard

A small Flask dashboard and command-line client for placing Market, Limit,
and Stop-Limit orders on Binance Futures Testnet (USDT-M). The application
keeps API signing, validation, order placement, and presentation separate so
the same trading logic is available from the browser and the terminal.

## Features

- **Order types:** MARKET, LIMIT, and STOP_LIMIT
- **Trading sides:** BUY and SELL
- **CLI input** via `argparse`, with validation before any API call
- **Dashboard:** account balance, positions, open orders, and connection checks
- **Logging:** rotating request, response, and error logs with secrets masked

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
├── app.py                 # Flask web application
├── api/index.py           # Vercel entry point
├── templates/index.html   # Dashboard markup
├── static/style.css       # Dashboard styles
├── requirements.txt
├── .env.example
├── .gitignore
└── logs/                  # Generated locally and ignored by Git
```

## Setup

1. **Clone the repository and install dependencies:**

   ```bash
  git clone https://github.com/raghav3907-svg/trading-bot.git
   cd trading_bot
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create Binance Futures Testnet credentials:**
  - Open https://testnet.binancefuture.com
  - Generate an HMAC-SHA256 API key and secret

3. **Configure credentials:**

   ```bash
   cp .env.example .env
   # then edit .env and paste your key/secret
   ```

   `.env` is git-ignored — never commit real API keys.

  This project is for Binance Futures Testnet. Do not use production
  credentials or production endpoints without a deliberate security review.

## Usage

### Web interface

Start the local website from the project folder:

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser. The web interface uses the
same local `.env` credentials and Binance Futures Testnet as the CLI.

### Deploy on Render

Create a Render Web Service from this repository. Render will use the included
`render.yaml` blueprint and start the app with Gunicorn. Add these environment
variables in the Render dashboard, without committing them to Git:

```text
BINANCE_API_KEY
BINANCE_API_SECRET
FLASK_SECRET_KEY
```

### Deploy on Vercel

This repository also includes a Vercel Python entry point. Import the GitHub
repository into Vercel, then add `BINANCE_API_KEY`, `BINANCE_API_SECRET`, and
`FLASK_SECRET_KEY` under Project Settings -> Environment Variables.

### CLI

Check the connection:

```bash
python cli.py --check-connection
```

Place orders with the commands shown below. Input is validated before any API
call, and detailed events are written to the rotating log file.

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
  --quantity 0.01 --price 61000 --stop-price 60800
```

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

## Validation

Run these lightweight local checks before publishing changes:

```bash
python -m compileall -q app.py api bot cli.py
python -c "from bot.validators import validate_order_params; print(validate_order_params('BTCUSDT', 'BUY', 'MARKET', 0.01))"
```

Live order commands require valid Binance Futures Testnet credentials and can
change the testnet account state.
