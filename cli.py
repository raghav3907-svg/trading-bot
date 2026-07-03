#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Examples:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

    python cli.py --symbol BTCUSDT --side SELL --type LIMIT \\
        --quantity 0.01 --price 60000

    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \\
        --quantity 0.01 --price 61000 --stop-price 60800

    python cli.py --check-connection
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceAPIError, BinanceNetworkError, FuturesTestnetClient
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Market/Limit/Stop-Limit orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument("--side", choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", type=float, help="Order quantity")
    parser.add_argument("--price", type=float, default=None, help="Price (required for LIMIT/STOP_LIMIT)")
    parser.add_argument("--stop-price", dest="stop_price", type=float, default=None,
                         help="Stop trigger price (required for STOP_LIMIT)")
    parser.add_argument("--check-connection", action="store_true",
                         help="Just ping the testnet and verify API keys, then exit")
    return parser


def main():
    load_dotenv()
    logger = setup_logging()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    parser = build_parser()
    args = parser.parse_args()

    try:
        client = FuturesTestnetClient(api_key, api_secret)
    except ValueError as exc:
        print(f"❌ Configuration error: {exc}")
        sys.exit(1)

    if args.check_connection:
        try:
            client.ping()
            account = client.get_account()
            print("✅ Connected to Binance Futures Testnet.")
            print(f"   Can trade: {account.get('canTrade')}")
        except (BinanceAPIError, BinanceNetworkError) as exc:
            print(f"❌ Connection check failed: {exc}")
            sys.exit(1)
        return

    missing = [name for name, val in
               [("--symbol", args.symbol), ("--side", args.side),
                ("--type", args.order_type), ("--quantity", args.quantity)]
               if val is None]
    if missing:
        parser.error(f"Missing required arguments: {', '.join(missing)}")

    try:
        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        print(f"❌ Invalid input: {exc}")
        sys.exit(1)
    except (BinanceAPIError, BinanceNetworkError):
        # already logged & printed inside place_order
        sys.exit(1)


if __name__ == "__main__":
    main()
