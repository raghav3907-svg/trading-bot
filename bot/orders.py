"""
Order placement logic: sits between the CLI and the raw API client.

Responsible for:
- validating input
- dispatching to the correct client method
- formatting a clean summary of the request and response
"""

import logging

from .client import BinanceAPIError, BinanceNetworkError, FuturesTestnetClient
from .validators import ValidationError, validate_order_params

logger = logging.getLogger("trading_bot.orders")


def build_request_summary(params: dict) -> str:
    lines = [
        "Order Request:",
        f"  Symbol     : {params['symbol']}",
        f"  Side       : {params['side']}",
        f"  Type       : {params['order_type']}",
        f"  Quantity   : {params['quantity']}",
    ]
    if params.get("price") is not None:
        lines.append(f"  Price      : {params['price']}")
    if params.get("stop_price") is not None:
        lines.append(f"  Stop Price : {params['stop_price']}")
    return "\n".join(lines)


def build_response_summary(response: dict) -> str:
    return "\n".join([
        "Order Response:",
        f"  Order ID     : {response.get('orderId')}",
        f"  Status       : {response.get('status')}",
        f"  Executed Qty : {response.get('executedQty')}",
        f"  Avg Price    : {response.get('avgPrice', 'N/A')}",
    ])


def place_order(
    client: FuturesTestnetClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
    stop_price=None,
) -> dict:
    """
    Validate parameters, place the order via the client, and log/print
    a clean summary. Returns the raw response dict from Binance.

    Raises ValidationError, BinanceAPIError, or BinanceNetworkError on failure.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    print(build_request_summary(params))
    logger.info("Placing order: %s", params)

    try:
        if params["order_type"] == "MARKET":
            response = client.place_market_order(params["symbol"], params["side"], params["quantity"])
        elif params["order_type"] == "LIMIT":
            response = client.place_limit_order(
                params["symbol"], params["side"], params["quantity"], params["price"]
            )
        else:  # STOP_LIMIT
            response = client.place_stop_limit_order(
                params["symbol"], params["side"], params["quantity"],
                params["price"], params["stop_price"],
            )
    except (BinanceAPIError, BinanceNetworkError) as exc:
        logger.error("Order failed: %s", exc)
        print(f"\n❌ Order FAILED: {exc}")
        raise

    print(build_response_summary(response))
    print("\n✅ Order placed successfully.")
    logger.info("Order succeeded: orderId=%s status=%s", response.get("orderId"), response.get("status"))
    return response
