import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Add the project root to sys.path to import from config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def create_dummy_data():
    """Populate MongoDB with dummy order data for testing the chatbot."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    print(f"Connecting to MongoDB at: {mongo_uri}")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.server_info()

        db = client["daraz"]
        collection = db["orders"]

        dummy_orders = [
            {
                "order_id": "ORD12345",
                "customer_name": "John Doe",
                "status": "Shipped",
                "items": ["Wireless Headphones", "USB-C Cable"],
                "total_amount": 55.00,
                "delivery_date": "2023-12-01",
                "shipping_address": "123 Main St, Dhaka"
            },
            {
                "order_id": "ORD67890",
                "customer_name": "Jane Smith",
                "status": "Processing",
                "items": ["Mechanical Keyboard"],
                "total_amount": 85.50,
                "delivery_date": "2023-12-05",
                "shipping_address": "456 Side Rd, Chittagong"
            },
            {
                "order_id": "ORD11223",
                "customer_name": "Alice Brown",
                "status": "Delivered",
                "items": ["Gaming Mouse", "Mousepad"],
                "total_amount": 40.00,
                "delivery_date": "2023-11-20",
                "shipping_address": "789 Park Ave, Sylhet"
            },
            {
                "order_id": "ORD44556",
                "customer_name": "Bob Wilson",
                "status": "Cancelled",
                "items": ["Webcam"],
                "total_amount": 30.00,
                "delivery_date": "N/A",
                "shipping_address": "321 Oak St, Rajshahi"
            }
        ]

        # Clear existing data
        collection.delete_many({})

        # Insert fresh dummy data
        result = collection.insert_many(dummy_orders)
        print(f"Successfully inserted {len(result.inserted_ids)} dummy orders into 'daraz.orders'.")

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("\nNote: Make sure your MongoDB instance is running and the MONGO_URI in .env is correct.")

if __name__ == "__main__":
    create_dummy_data()
