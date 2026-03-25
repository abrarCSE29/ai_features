"""Tools for the chatbot to interact with external systems."""

import os
from pymongo import MongoClient
from langchain.tools import tool
from config.app_config import AppConfig


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

        # Search for the order
        order = collection.find_one({"order_id": order_id})

        if order:
            # Remove MongoDB's _id for cleaner output
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
