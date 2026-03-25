# AI Features API

A modular FastAPI application for implementing various AI features with clean separation of concerns.

## Project Overview

This project implements AI-powered services using a modular architecture. Each feature is organized as an independent module, making the codebase scalable, maintainable, and easy to extend.

## Architecture

- **Modular Design**: Each AI feature (OCR, Chatbot, Object Detection) is implemented as a separate module
- **Router-based Organization**: Each module has its own router for endpoint management
- **Service Layer**: Business logic is separated into dedicated service classes
- **Pydantic Models**: Strong typing with request/response validation
- **Standardized Responses**: All endpoints use a unified `api_response` utility (`SuccessResponse` / `ErrorResponse`)

## Current Features

### OCR (Optical Character Recognition)
Extract text from PDF documents using PyMuPDF.

### Chatbot
Conversational AI assistant powered by Google Gemini and LangGraph. Supports multi-turn conversations with session memory, tool-calling for order lookup and placement, and product search with fuzzy matching.

**Available tools:**
- `search_order` — Look up an order by order ID
- `get_recent_orders` — List recent orders
- `list_products` — Browse products by category
- `get_product_categories` — List available product categories
- `search_products` — Fuzzy search products by keyword (e.g., "headphones", "shoes")
- `create_order` — Start an order for a product
- `confirm_order` — Confirm order details
- `finalize_order` — Place the order with email (sends confirmation email via Gmail SMTP)

### Object Detection
Detect objects in images using a YOLO model (YOLOv8). Supports filtering by object class, configurable confidence threshold, and returns per-object counts, bounding boxes, and an annotated image.

## Project Structure

```
ai_features/
├── config/
│   └── app_config.py              # Env-based configuration (CORS, API keys, DB, Redis, SMTP)
├── modules/
│   ├── chatbot/                   # Chatbot module
│   │   ├── service.py             # LangGraph ReAct agent + MemorySaver
│   │   ├── tools.py               # Order/product tools (MongoDB + Redis)
│   │   ├── models.py              # ChatRequest
│   │   └── router.py              # POST /chatbot/chat
│   ├── ocr/                       # OCR module
│   │   ├── service.py             # PyMuPDF text extraction
│   │   ├── models.py
│   │   └── router.py              # POST /ocr/extract-text
│   └── object_detection/          # Object Detection module
│       ├── service.py             # YOLO inference + image annotation
│       ├── models.py              # DetectionInfo, ObjectDetectionResult
│       └── router.py              # POST /object-detection/detect
├── utils/
│   ├── api_response/
│   │   ├── model.py               # SuccessResponse, ErrorResponse
│   │   └── service.py             # success(), error(), not_found(), etc.
│   └── logger/
│       └── logger.py              # Structured logger (structlog)
├── middleware/
│   ├── __init__.py                # Middleware setup
│   ├── exception_handler_middleware.py
│   └── request_id_middleware.py
├── static/                        # Static files (HTML visualization)
│   └── index.html                 # Object Detection web UI
├── scripts/
│   ├── setup_dummy_data.py        # Seeds MongoDB with dummy Daraz order data
│   ├── setup_products.py          # Seeds MongoDB with 25 products
│   └── yolo_to_onnx.py            # YOLO model conversion
├── logs/                          # Structured log files (auto-created)
├── main.py                        # FastAPI app entry point
├── pyproject.toml                 # Project config (uv/pip dependencies)
├── requirements.txt               # Project dependencies
├── docker-compose.yml             # Docker orchestration (MongoDB, Redis, App)
├── Dockerfile
└── README.md                      # This file
```

## Setup

### Option 1: Docker (Recommended)

The easiest way to run the application with all dependencies including MongoDB and Redis.

1. Clone the repository:
```bash
git clone https://github.com/abrarCSE29/ai_features.git
cd ai_features
```

2. Copy the example env file and fill in your values:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. Build and start all services:
```bash
docker compose up -d
```

This will start:
- **MongoDB** on port 3005
- **Redis** on port 6379
- **FastAPI App** on port 8000
- **Database setup** (populates dummy order data automatically)

4. Check logs to verify everything is working:
```bash
docker compose logs -f
```

5. Stop the services:
```bash
docker compose down
```

### Option 2: Local Development

1. Clone the repository:
```bash
git clone https://github.com/abrarCSE29/ai_features.git
cd ai_features
```

2. Install dependencies:
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

3. Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

4. Make sure MongoDB and Redis are running locally.

### Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key (required for chatbot) |
| `MONGO_URI` | MongoDB connection string (default: `mongodb://localhost:27017/`) |
| `REDIS_URI` | Redis connection string (default: `redis://localhost:6379/`) |
| `REDIS_DRAFT_ORDER_TTL` | Draft order expiry in seconds (default: `900`) |
| `SMTP_HOST` | SMTP server hostname (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP server port (default: `587`) |
| `SMTP_USER` | SMTP username (Gmail address) |
| `SMTP_PASSWORD` | SMTP password (Gmail App Password) |
| `SMTP_FROM_EMAIL` | Sender email address |
| `ORIGINS` | CORS allowed origins (default: `["*"]`) |
| `ALLOW_CREDENTIALS` | CORS allow credentials (default: `True`) |
| `ALLOWED_METHODS` | CORS allowed methods (default: `["*"]`) |
| `ALLOWED_HEADERS` | CORS allowed headers (default: `["*"]`) |

### Seed Dummy Data

```bash
# Seed orders (for chatbot tool-calling)
python scripts/setup_dummy_data.py

# Seed 25 products (for product search and ordering)
python scripts/setup_products.py
```

### Running the Application

```bash
uvicorn main:app --reload
```

## API Base URL

- **Local Development**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Standard Response Format

All endpoints return a unified response envelope:

**Success:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "...",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "status_code": 400,
  "error_code": "...",
  "message": "..."
}
```

## API Endpoints

### Health Check
- **`GET /health`**
- Returns `{ "status": "ai api running" }`

---

### OCR — Extract Text from PDF
- **`POST /ocr/extract-text`**
- **Parameters**: `file` (form-data) — PDF file
- **Success `data`**:
```json
{
  "filename": "document.pdf",
  "text": "Extracted text content..."
}
```

---

### Chatbot — Chat with AI Assistant
- **`POST /chatbot/chat`**
- **Body** (JSON):
```json
{
  "message": "What is the status of order ORD12345?",
  "session_id": "session_123"
}
```
- The `session_id` maintains conversation history across multiple requests.
- **Success `data`**:
```json
{
  "bot_response": "Your order ORD12345 has been shipped...",
  "session_id": "session_123"
}
```

**Example conversations:**

```
# Order lookup
User: "What's the status of order ORD12345?"
Bot:  "Order Found: {'order_id': 'ORD12345', 'status': 'Shipped', ...}"

# Product search
User: "Show me headphones"
Bot:  "Top results for 'headphones':
       - Sony WH-1000XM5 ... | Match: 100%
       - Apple AirPods Pro 2 ... | Match: 36%"

# Order placement (3-step flow)
User: "I want to buy Sony headphones"
Bot:  "Order Summary (Draft): Product: Sony WH-1000XM5 ... Please confirm."
User: "Yes"
Bot:  "Order confirmed! Please provide your email address."
User: "john@example.com"
Bot:  "Order placed successfully! Order ID: ORD48291 ... Confirmation email sent."
```

---

### Object Detection — Detect Objects in an Image
- **`POST /object-detection/detect`**
- **Parameters** (form-data):
  - `file` — Image file (JPEG, PNG, etc.)
  - `object_names` — JSON array string of object classes to detect (e.g., `["person", "car"]` or `person,car`)
  - `threshold` — Confidence threshold, float between 0 and 1 (default: `0.25`)
- **Success `data`**:
```json
{
  "detections": {
    "person": {
      "count": 2,
      "boxes": [[x1, y1, x2, y2, confidence], ...]
    },
    "car": {
      "count": 0,
      "boxes": []
    }
  },
  "annotated_image": "<base64-encoded JPEG>"
}
```
- The model (`yolo26m.pt`) is auto-downloaded on first use and cached in the `models/` directory.
- All requested object classes are always present in `detections`, even if count is 0.

**Visualization UI:**
- Visit **`/static/index.html`** for an interactive web interface to test object detection
- Features: Image upload preview, threshold slider, real-time results with annotated images and detection statistics

## Logging

Structured JSON logs are written to `logs/ai-features-YYYY-MM-DD.log`. Useful for debugging chatbot tool calls and order placement issues.

```bash
# Find order-related logs
grep "create_order\|confirm_order\|finalize_order" logs/ai-features-*.log

# Find errors only
grep '"error"' logs/ai-features-*.log
```

## Technologies

| Technology | Purpose |
|---|---|
| FastAPI + Uvicorn | Web framework & ASGI server |
| LangGraph + LangChain | Chatbot agent, tool-calling, session memory |
| Google Gemini (`gemini-2.5-flash`) | LLM for chatbot |
| MongoDB + PyMongo | Product and order database |
| Redis | Draft order state during checkout |
| rapidfuzz | Fuzzy product name matching |
| smtplib (Gmail SMTP) | Order confirmation emails |
| PyMuPDF (`fitz`) | PDF text extraction |
| Ultralytics YOLO | Object detection model |
| OpenCV + NumPy | Image processing & annotation |
| Pydantic | Data validation |
| structlog | Structured logging |
| python-dotenv | Environment variable management |
