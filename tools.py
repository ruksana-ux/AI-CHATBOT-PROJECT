"""Data helpers: FAQ loading and order-status lookup."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def _get_file_path(filename: str) -> Path:
    """Find file in root directory or data/."""
    if (BASE_DIR / filename).exists():
        return BASE_DIR / filename
    return DATA_DIR / filename


def load_faqs() -> list[dict]:
    """Load FAQ entries from JSON file."""
    path = _get_file_path("faqs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_orders() -> list[dict]:
    """Load sample orders from JSON file."""
    path = _get_file_path("orders.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_order_status(order_id: str, email: str) -> dict:
    """
    Validate the order number and customer identity (email) before returning order information.
    Retrieves order status, estimated delivery date, and product details.
    """
    order_id = (order_id or "").strip().upper()
    email = (email or "").strip().lower()

    if not order_id:
        return {
            "success": False,
            "error": "Missing order number. Please provide a valid order ID (e.g., ORD1002)."
        }

    if not email:
        return {
            "success": False,
            "error": "Missing customer identity. Please provide the email address used for this order to verify your identity."
        }

    orders = load_orders()
    for order in orders:
        if order.get("order_id", "").strip().upper() == order_id:
            # Validate customer identity
            if order.get("email", "").strip().lower() != email:
                return {
                    "success": False,
                    "error": "Customer identity verification failed. The provided email does not match our records for this order."
                }
            # Support both singular 'product' and plural 'products' list
            product_val = order.get("product")
            products_list = order.get("products")
            if not product_val and products_list:
                if isinstance(products_list, list):
                    product_val = ", ".join(products_list)
                else:
                    product_val = str(products_list)

            return {
                "success": True,
                "order_id": order["order_id"],
                "customer_name": order.get("customer_name"),
                "product": product_val,
                "products": products_list or ([product_val] if product_val else []),
                "quantity": order.get("quantity"),
                "status": order.get("status"),
                "estimated_delivery": order.get("estimated_delivery"),
            }

    return {
        "success": False,
        "error": f"No order found with order ID '{order_id}'."
    }
