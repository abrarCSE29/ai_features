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
