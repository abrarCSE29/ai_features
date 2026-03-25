"""Tools for the chatbot to interact with external systems."""

import json
import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pymongo import MongoClient
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from config.app_config import AppConfig
from utils.logger.logger import Logger

logger = Logger()

DUMMY_SHIPPING_ADDRESS = "123 Default St, Dhaka 1205"
DUMMY_PHONE = "+8801700000000"


def _get_draft_key(thread_id: str) -> str:
    return f"draft_order:{thread_id}"


def _get_redis():
    import redis

    logger.info(message="Connecting to Redis", redis_uri=AppConfig.redis_uri)
    client = redis.from_url(AppConfig.redis_uri, decode_responses=True)
    logger.info(message="Redis connection established")
    return client


def _send_order_email(
    to_email: str, customer_name: str, order_id: str, draft: dict
) -> str:
    if not AppConfig.smtp_user or not AppConfig.smtp_password:
        logger.warning(message="_send_order_email: SMTP not configured, skipping")
        return "skipped: SMTP not configured"

    subject = f"Order Confirmation - {order_id}"

    text_body = (
        f"Hi {customer_name},\n\n"
        f"Your order has been placed successfully!\n\n"
        f"Order ID:          {order_id}\n"
        f"Product:           {draft['product_name']}\n"
        f"Quantity:          {draft['quantity']}\n"
        f"Total:             ${draft['total_amount']:.2f}\n"
        f"Shipping Address:  {draft['shipping_address']}\n"
        f"Status:            Processing\n\n"
        f"Thank you for shopping with Daraz!"
    )

    html_body = f"""\
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
  <h2>Order Confirmation</h2>
  <p>Hi {customer_name},</p>
  <p>Your order has been placed successfully!</p>
  <table style="border-collapse: collapse; width: 100%; max-width: 480px;">
    <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Order ID</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_id}</td></tr>
    <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Product</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{draft["product_name"]}</td></tr>
    <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Quantity</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{draft["quantity"]}</td></tr>
    <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Total</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">${draft["total_amount"]:.2f}</td></tr>
    <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Shipping</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{draft["shipping_address"]}</td></tr>
    <tr><td style="padding: 8px;"><strong>Status</strong></td>
        <td style="padding: 8px;">Processing</td></tr>
  </table>
  <p style="margin-top: 20px;">Thank you for shopping with <strong>Daraz</strong>!</p>
</body>
</html>"""

    try:
        logger.info(
            message="_send_order_email: sending email",
            to=to_email,
            smtp_host=AppConfig.smtp_host,
            smtp_port=AppConfig.smtp_port,
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = AppConfig.smtp_from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(AppConfig.smtp_host, AppConfig.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(AppConfig.smtp_user, AppConfig.smtp_password)
            server.sendmail(AppConfig.smtp_from_email, to_email, msg.as_string())

        logger.info(message="_send_order_email: email sent successfully", to=to_email)
        return "sent"

    except smtplib.SMTPException as e:
        logger.error(
            message="_send_order_email: SMTP error",
            error_type=type(e).__name__,
            error=str(e),
        )
        return f"failed: {str(e)}"
    except Exception as e:
        logger.error(
            message="_send_order_email: unexpected error",
            error_type=type(e).__name__,
            error=str(e),
        )
        return f"failed: {str(e)}"


@tool
def search_order(order_id: str) -> str:
    """
    Search for a specific order in the database using the order ID.
    Returns the order details if found, or an error message if not.
    """
    try:
        client = MongoClient(AppConfig.mongo_uri)
        db = client["daraz"]
        collection = db["orders"]

        order = collection.find_one({"order_id": order_id})

        if order:
            if "_id" in order:
                del order["_id"]
            return f"Order Found: {str(order)}"
        else:
            return f"Order with ID '{order_id}' not found."

    except Exception as e:
        return f"Error accessing database: {str(e)}"
    finally:
        client.close()


@tool
def list_products(category: str = "", limit: int = 10) -> str:
    """
    List products available on Daraz, optionally filtered by category.
    Use this when the user asks about available products, product listings, or wants to browse by category.
    Each product has: name, category, vendor_name, stock, rating, price.
    Args:
        category: Filter by product category (e.g., "Electronics", "Fashion"). Leave empty to list all.
        limit: Maximum number of products to return (default 10).
    """
    try:
        client = MongoClient(AppConfig.mongo_uri)
        db = client["daraz"]
        collection = db["products"]

        query = {}
        if category:
            query["category"] = {"$regex": category, "$options": "i"}

        products = list(collection.find(query, {"_id": 0}).limit(limit))

        if not products:
            return f"No products found{' in category ' + category if category else ''}."

        formatted = "\n".join(
            f"- {p['name']} | Category: {p['category']} | Vendor: {p['vendor_name']} "
            f"| Price: ${p['price']:.2f} | Stock: {p['stock']} | Rating: {p['rating']}"
            for p in products
        )
        return f"Products{' in ' + category if category else ''}:\n{formatted}"

    except Exception as e:
        return f"Error fetching products: {str(e)}"
    finally:
        client.close()


@tool
def create_order(
    product_name: str, quantity: int = 1, config: RunnableConfig = None
) -> str:
    """
    Start placing an order for a product.
    Use this when the user wants to buy or order a specific product.
    The user must confirm the order details before it can be placed.
    Args:
        product_name: The exact or partial name of the product to order.
        quantity: Number of items to order (default 1).
        config: Automatically passed by the system — do not provide this.
    """
    logger.info(
        message="create_order called",
        product_name=product_name,
        quantity=quantity,
    )

    if config is None:
        logger.error(message="create_order: config is None — no session context")
        return "Internal error: session context not available."

    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        logger.error(message="create_order: thread_id missing from config")
        return "Internal error: missing session identifier."

    logger.info(message="create_order: session identified", thread_id=thread_id)

    mongo_client = None
    redis_client = None
    try:
        mongo_client = MongoClient(AppConfig.mongo_uri)
        db = mongo_client["daraz"]
        collection = db["products"]

        logger.info(
            message="create_order: searching for product",
            product_name=product_name,
        )

        product = collection.find_one(
            {"name": {"$regex": product_name, "$options": "i"}}, {"_id": 0}
        )

        if not product:
            logger.warning(
                message="create_order: product not found",
                product_name=product_name,
            )
            return f"Product matching '{product_name}' not found. Try searching first with 'search_products'."

        logger.info(
            message="create_order: product found",
            product_name=product["name"],
            price=product["price"],
            stock=product.get("stock"),
        )

        if product.get("stock", 0) < quantity:
            logger.warning(
                message="create_order: insufficient stock",
                product_name=product["name"],
                available=product["stock"],
                requested=quantity,
            )
            return (
                f"Insufficient stock for '{product['name']}'. "
                f"Available: {product['stock']}, Requested: {quantity}."
            )

        total_amount = round(product["price"] * quantity, 2)

        draft = {
            "product_name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "total_amount": total_amount,
            "status": "draft",
            "items": [product["name"]],
            "shipping_address": DUMMY_SHIPPING_ADDRESS,
            "phone": DUMMY_PHONE,
        }

        draft_key = _get_draft_key(thread_id)
        logger.info(
            message="create_order: storing draft in Redis",
            draft_key=draft_key,
            draft=draft,
        )

        redis_client = _get_redis()
        redis_client.setex(
            draft_key,
            AppConfig.redis_draft_order_ttl,
            json.dumps(draft),
        )

        logger.info(
            message="create_order: draft stored successfully",
            draft_key=draft_key,
            ttl=AppConfig.redis_draft_order_ttl,
        )

        return (
            f"Order Summary (Draft):\n"
            f"Product: {product['name']}\n"
            f"Price: ${product['price']:.2f}\n"
            f"Quantity: {quantity}\n"
            f"Total: ${total_amount:.2f}\n"
            f"Shipping Address: {DUMMY_SHIPPING_ADDRESS}\n"
            f"Phone: {DUMMY_PHONE}\n"
            f"Status: Draft\n\n"
            f"Please confirm to proceed. Say 'yes' or 'confirm' to continue."
        )

    except Exception as e:
        logger.error(
            message="create_order: exception occurred",
            error_type=type(e).__name__,
            error=str(e),
        )
        return f"Error creating order: {str(e)}"
    finally:
        if mongo_client:
            mongo_client.close()
        if redis_client:
            redis_client.close()


@tool
def confirm_order(config: RunnableConfig = None) -> str:
    """
    Confirm the order details before placing the order.
    Use this when the user says 'yes', 'confirm', or agrees to the order summary.
    Args:
        config: Automatically passed by the system — do not provide this.
    """
    logger.info(message="confirm_order called")

    if config is None:
        logger.error(message="confirm_order: config is None — no session context")
        return "Internal error: session context not available."

    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        logger.error(message="confirm_order: thread_id missing from config")
        return "Internal error: missing session identifier."

    logger.info(message="confirm_order: session identified", thread_id=thread_id)

    redis_client = None
    try:
        redis_client = _get_redis()
        draft_key = _get_draft_key(thread_id)

        logger.info(
            message="confirm_order: reading draft from Redis", draft_key=draft_key
        )
        raw = redis_client.get(draft_key)

        if not raw:
            logger.warning(
                message="confirm_order: no draft found in Redis",
                draft_key=draft_key,
            )
            return "No pending order found. Start a new order first."

        draft = json.loads(raw)
        logger.info(
            message="confirm_order: draft loaded",
            draft_key=draft_key,
            status=draft.get("status"),
            product_name=draft.get("product_name"),
        )

        if draft.get("status") == "confirmed":
            logger.info(
                message="confirm_order: order already confirmed",
                draft_key=draft_key,
            )
            return (
                "Order is already confirmed. "
                "Please provide your email address to finalize."
            )

        if draft.get("status") != "draft":
            logger.warning(
                message="confirm_order: unexpected draft status",
                draft_key=draft_key,
                status=draft.get("status"),
            )
            return f"Cannot confirm order with status '{draft.get('status')}'."

        draft["status"] = "confirmed"
        redis_client.setex(
            draft_key,
            AppConfig.redis_draft_order_ttl,
            json.dumps(draft),
        )

        logger.info(
            message="confirm_order: order confirmed, draft updated in Redis",
            draft_key=draft_key,
            product_name=draft["product_name"],
            total_amount=draft["total_amount"],
        )

        return (
            f"Order confirmed! Please provide your email address to finalize the order.\n\n"
            f"Order Details:\n"
            f"Product: {draft['product_name']}\n"
            f"Quantity: {draft['quantity']}\n"
            f"Total: ${draft['total_amount']:.2f}"
        )

    except Exception as e:
        logger.error(
            message="confirm_order: exception occurred",
            error_type=type(e).__name__,
            error=str(e),
        )
        return f"Error confirming order: {str(e)}"
    finally:
        if redis_client:
            redis_client.close()


@tool
def finalize_order(email: str, config: RunnableConfig = None) -> str:
    """
    Finalize the order with the user's email address and place it.
    Use this when the user provides their email address after confirming the order.
    Args:
        email: The user's email address for order confirmation.
        config: Automatically passed by the system — do not provide this.
    """
    logger.info(message="finalize_order called", email=email)

    if config is None:
        logger.error(message="finalize_order: config is None — no session context")
        return "Internal error: session context not available."

    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        logger.error(message="finalize_order: thread_id missing from config")
        return "Internal error: missing session identifier."

    logger.info(message="finalize_order: session identified", thread_id=thread_id)

    redis_client = None
    mongo_client = None
    try:
        redis_client = _get_redis()
        draft_key = _get_draft_key(thread_id)

        logger.info(
            message="finalize_order: reading draft from Redis", draft_key=draft_key
        )
        raw = redis_client.get(draft_key)

        if not raw:
            logger.warning(
                message="finalize_order: no draft found in Redis",
                draft_key=draft_key,
            )
            return "No pending order found. Start a new order first."

        draft = json.loads(raw)
        logger.info(
            message="finalize_order: draft loaded",
            draft_key=draft_key,
            status=draft.get("status"),
            product_name=draft.get("product_name"),
        )

        if draft.get("status") == "draft":
            logger.warning(
                message="finalize_order: order not yet confirmed",
                draft_key=draft_key,
            )
            return "Order not confirmed yet. Please confirm the order details first."

        if draft.get("status") != "confirmed":
            logger.warning(
                message="finalize_order: unexpected draft status",
                draft_key=draft_key,
                status=draft.get("status"),
            )
            return f"Cannot finalize order with status '{draft.get('status')}'."

        order_id = f"ORD{random.randint(10000, 99999)}"
        customer_name = email.split("@")[0]

        order = {
            "order_id": order_id,
            "customer_name": customer_name,
            "email": email,
            "phone": draft["phone"],
            "status": "Processing",
            "items": draft["items"],
            "total_amount": draft["total_amount"],
            "delivery_date": "TBD",
            "shipping_address": draft["shipping_address"],
        }

        logger.info(
            message="finalize_order: inserting order into MongoDB",
            order_id=order_id,
            collection="daraz.orders",
            order=order,
        )

        mongo_client = MongoClient(AppConfig.mongo_uri)
        db = mongo_client["daraz"]
        db["orders"].insert_one(order)

        logger.info(
            message="finalize_order: order inserted into MongoDB",
            order_id=order_id,
        )

        redis_client.delete(draft_key)
        logger.info(
            message="finalize_order: draft deleted from Redis",
            draft_key=draft_key,
        )

        email_result = _send_order_email(email, customer_name, order_id, draft)
        logger.info(
            message="finalize_order: email result",
            email_result=email_result,
        )

        if email_result == "sent":
            email_status = f"Confirmation email sent to {email}."
        elif email_result.startswith("skipped"):
            email_status = (
                "Email not configured — order confirmed without notification."
            )
        else:
            email_status = "Order placed. Email delivery failed — we'll retry shortly."

        logger.info(
            message="finalize_order: order placement complete",
            order_id=order_id,
            email=email,
            total_amount=draft["total_amount"],
        )

        return (
            f"Order placed successfully!\n\n"
            f"Order ID: {order_id}\n"
            f"Product: {draft['product_name']}\n"
            f"Quantity: {draft['quantity']}\n"
            f"Total: ${draft['total_amount']:.2f}\n"
            f"Email: {email}\n"
            f"Shipping Address: {draft['shipping_address']}\n"
            f"Status: Processing\n\n"
            f"{email_status}\n\n"
            f"Thank you for shopping with Daraz!"
        )

    except Exception as e:
        logger.error(
            message="finalize_order: exception occurred",
            error_type=type(e).__name__,
            error=str(e),
        )
        return f"Error finalizing order: {str(e)}"
    finally:
        if redis_client:
            redis_client.close()
        if mongo_client:
            mongo_client.close()


@tool
def get_product_categories() -> str:
    """
    Get all available product categories on Daraz.
    Use this when the user asks what categories of products are available.
    """
    try:
        client = MongoClient(AppConfig.mongo_uri)
        db = client["daraz"]
        collection = db["products"]

        categories = collection.distinct("category")

        if not categories:
            return "No product categories found in the database."

        return "Available categories: " + ", ".join(sorted(categories))

    except Exception as e:
        return f"Error fetching categories: {str(e)}"
    finally:
        client.close()


@tool
def search_products(query: str, limit: int = 7) -> str:
    """
    Search for products by keyword with fuzzy matching.
    Use this when the user searches for a product by name or keyword
    and does not know the exact product name (e.g., "headphones", "keyboard", "shoes").
    Args:
        query: The search keyword or partial product name (e.g., "headphones", "wireless mouse").
        limit: Maximum number of results to return (default 7).
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        return "Product search is currently unavailable."

    try:
        client = MongoClient(AppConfig.mongo_uri)
        db = client["daraz"]
        collection = db["products"]

        # Build $regex from query words for server-side pre-filtering
        words = query.split()
        regex_pattern = "|".join(word for word in words if word)
        if not regex_pattern:
            return "Please provide a search term."

        query_filter = {
            "$or": [
                {"name": {"$regex": regex_pattern, "$options": "i"}},
                {"category": {"$regex": regex_pattern, "$options": "i"}},
            ]
        }

        candidates = list(collection.find(query_filter, {"_id": 0}))

        if not candidates:
            return f"No products found matching '{query}'."

        # Score each candidate with fuzzy matching
        scored = []
        for product in candidates:
            score = fuzz.token_set_ratio(query.lower(), product["name"].lower())
            scored.append((score, product))

        # Sort by fuzzy score descending, then by rating as tiebreaker
        scored.sort(key=lambda x: (-x[0], -x[1].get("rating", 0)))

        # Keep only results above minimum relevance threshold
        results = [(s, p) for s, p in scored if s >= 40][:limit]

        if not results:
            return f"No products found matching '{query}'."

        formatted = "\n".join(
            f"- {p['name']} | Category: {p['category']} | Vendor: {p['vendor_name']} "
            f"| Price: ${p['price']:.2f} | Stock: {p['stock']} | Rating: {p['rating']} "
            f"| Match: {s}%"
            for s, p in results
        )
        return f"Top results for '{query}':\n{formatted}"

    except Exception as e:
        return f"Error searching products: {str(e)}"
    finally:
        client.close()


@tool
def get_recent_orders(limit: int = 5) -> str:
    """
    Retrieve the most recent orders from the database.
    Returns a list of recent orders or an error message.
    """
    try:
        client = MongoClient(AppConfig.mongo_uri)
        db = client["daraz"]
        collection = db["orders"]

        # In a real app, we'd sort by date. For this dummy data, we'll just take the latest entries.
        orders = list(collection.find().limit(limit))

        if orders:
            for order in orders:
                if "_id" in order:
                    del order["_id"]
            return f"Recent Orders: {str(orders)}"
        else:
            return "No orders found in the database."

    except Exception as e:
        return f"Error accessing database: {str(e)}"
    finally:
        client.close()
