#!/usr/bin/env python3
"""Web entry point for the Binance Futures Testnet trading bot."""

import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from bot.client import BinanceAPIError, BinanceNetworkError, FuturesTestnetClient
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import ValidationError

load_dotenv()
setup_logging()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "local-development-key")


def get_client() -> FuturesTestnetClient:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET are required in .env")
    return FuturesTestnetClient(api_key, api_secret)


@app.get("/")
def index():
    dashboard = {"account": None, "open_orders": [], "positions": [], "error": None}
    try:
        client = get_client()
        dashboard["account"] = client.get_account()
        dashboard["open_orders"] = client.get_open_orders()
        dashboard["positions"] = [
            position for position in client.get_position_risk()
            if float(position.get("positionAmt", 0)) != 0
        ]
    except (ValueError, BinanceAPIError, BinanceNetworkError) as exc:
        dashboard["error"] = str(exc)
    return render_template("index.html", dashboard=dashboard)


@app.post("/connection")
def connection():
    try:
        client = get_client()
        client.ping()
        account = client.get_account()
        flash(f"Connected to Binance Futures Testnet. Can trade: {account.get('canTrade')}", "success")
    except (ValueError, BinanceAPIError, BinanceNetworkError) as exc:
        flash(f"Connection failed: {exc}", "error")
    return redirect(url_for("index"))


@app.post("/orders")
def orders():
    try:
        client = get_client()
        order_type = request.form.get("order_type", "").upper()
        response = place_order(
            client=client,
            symbol=request.form.get("symbol", ""),
            side=request.form.get("side", ""),
            order_type=order_type,
            quantity=request.form.get("quantity"),
            price=request.form.get("price") or None,
            stop_price=request.form.get("stop_price") or None,
        )
        flash(
            f"Order placed: {response.get('orderId')} ({response.get('status')})",
            "success",
        )
    except (ValueError, ValidationError, BinanceAPIError, BinanceNetworkError) as exc:
        flash(f"Order failed: {exc}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)