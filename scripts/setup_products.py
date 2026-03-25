import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


def create_products():
    """Populate MongoDB with dummy product data for testing the chatbot."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    print(f"Connecting to MongoDB at: {mongo_uri}")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()

        db = client["daraz"]
        collection = db["products"]

        products = [
            {
                "name": "Sony WH-1000XM5 Wireless Headphones",
                "category": "Electronics",
                "vendor_name": "TechWorld BD",
                "stock": 120,
                "rating": 4.8,
                "price": 279.99,
            },
            {
                "name": "Logitech MX Master 3S Mouse",
                "category": "Electronics",
                "vendor_name": "TechWorld BD",
                "stock": 85,
                "rating": 4.7,
                "price": 99.99,
            },
            {
                "name": "Samsung 65-inch 4K Smart TV",
                "category": "Electronics",
                "vendor_name": "Samsung Official",
                "stock": 30,
                "rating": 4.5,
                "price": 799.99,
            },
            {
                "name": "USB-C Charging Cable 2m",
                "category": "Accessories",
                "vendor_name": "CableKing",
                "stock": 500,
                "rating": 4.2,
                "price": 9.99,
            },
            {
                "name": "Anker 20000mAh Power Bank",
                "category": "Accessories",
                "vendor_name": "Anker Official",
                "stock": 200,
                "rating": 4.6,
                "price": 49.99,
            },
            {
                "name": "Razer BlackWidow V4 Mechanical Keyboard",
                "category": "Electronics",
                "vendor_name": "TechWorld BD",
                "stock": 60,
                "rating": 4.6,
                "price": 169.99,
            },
            {
                "name": "Levi's 501 Original Fit Jeans",
                "category": "Fashion",
                "vendor_name": "Levi's Official",
                "stock": 150,
                "rating": 4.4,
                "price": 69.99,
            },
            {
                "name": "Nike Air Max 90 Sneakers",
                "category": "Fashion",
                "vendor_name": "Nike Official",
                "stock": 75,
                "rating": 4.7,
                "price": 129.99,
            },
            {
                "name": "Adidas Ultraboost 23 Running Shoes",
                "category": "Fashion",
                "vendor_name": "Adidas Official",
                "stock": 90,
                "rating": 4.8,
                "price": 189.99,
            },
            {
                "name": "Casio G-Shock GA-2100 Watch",
                "category": "Fashion",
                "vendor_name": "WatchHub",
                "stock": 110,
                "rating": 4.5,
                "price": 99.99,
            },
            {
                "name": "Instant Pot Duo 7-in-1 Pressure Cooker",
                "category": "Home & Kitchen",
                "vendor_name": "HomePlus",
                "stock": 40,
                "rating": 4.7,
                "price": 89.99,
            },
            {
                "name": "Dyson V12 Detect Slim Vacuum",
                "category": "Home & Kitchen",
                "vendor_name": "Dyson Official",
                "stock": 25,
                "rating": 4.6,
                "price": 649.99,
            },
            {
                "name": "Philips Hue Smart Bulb Starter Kit",
                "category": "Home & Kitchen",
                "vendor_name": "HomePlus",
                "stock": 180,
                "rating": 4.4,
                "price": 199.99,
            },
            {
                "name": "The North Face Borealis Backpack",
                "category": "Fashion",
                "vendor_name": "OutdoorGear",
                "stock": 65,
                "rating": 4.6,
                "price": 99.99,
            },
            {
                "name": "Apple AirPods Pro 2",
                "category": "Electronics",
                "vendor_name": "Apple Official",
                "stock": 200,
                "rating": 4.8,
                "price": 249.99,
            },
            {
                "name": "Dell 27-inch 4K USB-C Monitor",
                "category": "Electronics",
                "vendor_name": "Dell Official",
                "stock": 45,
                "rating": 4.5,
                "price": 449.99,
            },
            {
                "name": "Olay Regenerist Micro-Sculpting Cream",
                "category": "Beauty",
                "vendor_name": "BeautyMart",
                "stock": 300,
                "rating": 4.3,
                "price": 34.99,
            },
            {
                "name": "CeraVe Hydrating Facial Cleanser",
                "category": "Beauty",
                "vendor_name": "BeautyMart",
                "stock": 250,
                "rating": 4.6,
                "price": 14.99,
            },
            {
                "name": "LEGO Star Wars Millennium Falcon",
                "category": "Toys & Games",
                "vendor_name": "ToyLand",
                "stock": 35,
                "rating": 4.9,
                "price": 169.99,
            },
            {
                "name": "Hasbro Monopoly Classic Board Game",
                "category": "Toys & Games",
                "vendor_name": "ToyLand",
                "stock": 100,
                "rating": 4.4,
                "price": 19.99,
            },
            {
                "name": "YETI Rambler 36oz Water Bottle",
                "category": "Accessories",
                "vendor_name": "OutdoorGear",
                "stock": 130,
                "rating": 4.7,
                "price": 44.99,
            },
            {
                "name": "Skechers GOwalk 5 Walking Shoes",
                "category": "Fashion",
                "vendor_name": "Skechers Official",
                "stock": 95,
                "rating": 4.3,
                "price": 74.99,
            },
            {
                "name": "Ninja Professional 72oz Blender",
                "category": "Home & Kitchen",
                "vendor_name": "HomePlus",
                "stock": 55,
                "rating": 4.5,
                "price": 89.99,
            },
            {
                "name": "Samsung Galaxy S24 Ultra Case",
                "category": "Accessories",
                "vendor_name": "TechWorld BD",
                "stock": 400,
                "rating": 4.1,
                "price": 24.99,
            },
            {
                "name": "Spotify Car Thing Wireless Adapter",
                "category": "Electronics",
                "vendor_name": "AudioHub",
                "stock": 70,
                "rating": 4.0,
                "price": 49.99,
            },
        ]

        collection.delete_many({})

        result = collection.insert_many(products)
        print(
            f"Successfully inserted {len(result.inserted_ids)} products into 'daraz.products'."
        )

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print(
            "\nNote: Make sure your MongoDB instance is running and the MONGO_URI in .env is correct."
        )


if __name__ == "__main__":
    create_products()
