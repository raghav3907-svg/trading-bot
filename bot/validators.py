"""
Input validation for order parameters.

Keeping validation separate from the CLI and client layers makes it
independently testable and keeps error messages consistent.
"""

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}

# Basic sanity check: symbol should be uppercase letters/numbers, e.g. BTCUSDT
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(Exception):
    """Raised when user-supplied order parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _SYMBOL_RE.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected format like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {VALID_ORDER_TYPES}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError(f"Quantity must be positive, got {quantity}.")
    return quantity


def validate_price(price, required: bool) -> float | None:
    if price is None:
        if required:
            raise ValidationError("Price is required for LIMIT / STOP_LIMIT orders.")
        return None
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price must be a number, got '{price}'.")
    if price <= 0:
        raise ValidationError(f"Price must be positive, got {price}.")
    return price


def validate_stop_price(stop_price, order_type: str) -> float | None:
    if order_type != "STOP_LIMIT":
        return None
    if stop_price is None:
        raise ValidationError("Stop price is required for STOP_LIMIT orders.")
    try:
        stop_price = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
    if stop_price <= 0:
        raise ValidationError(f"Stop price must be positive, got {stop_price}.")
    return stop_price


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
    stop_price=None,
) -> dict:
    """Validate a full set of order parameters and return normalized values."""
    order_type = validate_order_type(order_type)
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": order_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, required=order_type in ("LIMIT", "STOP_LIMIT")),
        "stop_price": validate_stop_price(stop_price, order_type),
    }
