"""
Thin REST client wrapper around Binance Futures Testnet (USDT-M).

Only the endpoints needed for this assignment are implemented:
- placing orders (MARKET / LIMIT / STOP)
- checking account/server connectivity

All requests and responses are logged. Signing follows Binance's
HMAC-SHA256 query-string signing scheme.
"""

import hashlib
import hmac
import logging
import time
from typing import cast
from urllib.parse import urlencode

import requests

BASE_URL = "https://demo-fapi.binance.com"


class BinanceAPIError(Exception):
    """Raised when Binance returns an error response."""

    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"Binance API error [{status_code}]: {payload}")


class BinanceNetworkError(Exception):
    """Raised on connection failures, timeouts, etc."""


class FuturesTestnetClient:
    """Minimal Binance USDT-M Futures Testnet REST client."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be provided (check your .env file).")
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger("trading_bot.client")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        self.time_offset = 0
        try:
            self._sync_time()
        except Exception:
            pass  # fall back to local clock

    # ---------- internals ----------

    def _sync_time(self):
        """Align local clock with Binance server time."""
        r = self.session.get(f"{self.base_url}/fapi/v1/time", timeout=self.timeout)
        server_ms = r.json()["serverTime"]
        self.time_offset = server_ms - int(time.time() * 1000)
        self.logger.info("Synced server time, offset=%sms", self.time_offset)

    def _sign(self, params: dict) -> dict:
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000) + self.time_offset
        params["recvWindow"] = params.get("recvWindow", 5000)
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, path: str, params: dict, signed: bool = True) -> dict:
        url = f"{self.base_url}{path}"
        req_params = self._sign(params) if signed else params

        self.logger.debug("REQUEST %s %s params=%s", method, url, {**req_params, "signature": "***"} if signed else req_params)

        try:
            response = self.session.request(method, url, params=req_params, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            self.logger.error("NETWORK ERROR on %s %s: %s", method, url, exc)
            raise BinanceNetworkError(str(exc)) from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_text": response.text}

        if response.status_code != 200:
            self.logger.error("RESPONSE ERROR %s %s -> status=%s payload=%s", method, url, response.status_code, payload)
            raise BinanceAPIError(response.status_code, payload)

        self.logger.debug("RESPONSE OK %s %s -> %s", method, url, payload)
        return payload

    # ---------- public API ----------

    def ping(self) -> dict:
        """Check connectivity to the testnet server (unsigned)."""
        return self._request("GET", "/fapi/v1/ping", {}, signed=False)

    def get_account(self) -> dict:
        """Fetch account info (signed) — useful to verify API keys work."""
        return self._request("GET", "/fapi/v2/account", {})

    def get_open_orders(self, symbol: str | None = None) -> list:
        """Fetch currently open orders, optionally filtered by symbol."""
        params = {"symbol": symbol} if symbol else {}
        return cast(list, self._request("GET", "/fapi/v1/openOrders", params))

    def get_position_risk(self, symbol: str | None = None) -> list:
        """Fetch position risk data, optionally filtered by symbol."""
        params = {"symbol": symbol} if symbol else {}
        return cast(list, self._request("GET", "/fapi/v2/positionRisk", params))

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
        }
        return self._request("POST", "/fapi/v1/order", params)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float,
                           time_in_force: str = "GTC") -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
        }
        return self._request("POST", "/fapi/v1/order", params)

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                                price: float, stop_price: float,
                                time_in_force: str = "GTC") -> dict:
        """Bonus order type: STOP (stop-limit) futures order."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
            "timeInForce": time_in_force,
        }
        return self._request("POST", "/fapi/v1/order", params)