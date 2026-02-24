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
Conversational AI assistant powered by Google Gemini and LangGraph. Supports multi-turn conversations with session memory and tool-calling to look up order data from MongoDB.

### Object Detection
Detect objects in images using a YOLO model (YOLOv8). Supports filtering by object class, configurable confidence threshold, and returns per-object counts, bounding boxes, and an annotated image.

## Project Structure

```
ai_features/
├── config/
│   └── app_config.py              # Env-based configuration (CORS, API keys, DB)
├── modules/
│   ├── chatbot/                   # Chatbot module
│   │   ├── chatbot_service.py     # LangGraph ReAct agent + MemorySaver
│   │   ├── tools.py               # search_order, get_recent_orders (MongoDB)
│   │   ├── models.py              # ChatRequest
│   │   └── router.py              # POST /chatbot/chat
│   ├── ocr/                       # OCR module
│   │   ├── service.py             # PyMuPDF text extraction
│   │   ├── models.py              # (standardized responses used)
│   │   └── router.py              # POST /ocr/extract-text
│   └── object_detection/          # Object Detection module
│       ├── service.py             # YOLO inference + image annotation
│       ├── models.py              # DetectionInfo, ObjectDetectionResult
│       └── router.py              # POST /object-detection/detect
├── utils/
│   └── api_response/
│       ├── model.py               # SuccessResponse, ErrorResponse
│       └── service.py             # success(), error(), not_found(), etc.
├── static/                        # Static files (HTML visualization)
│   └── index.html                 # Object Detection web UI
├── scripts/
│   └── setup_dummy_data.py        # Seeds MongoDB with dummy Daraz order data
├── main.py                        # FastAPI app entry point
├── requirements.txt               # Project dependencies
└── README.md                      # This file
```

## Setup

### Option 1: Docker (Recommended)

The easiest way to run the application with all dependencies including MongoDB.

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

### Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key (required for chatbot) |
| `MONGO_URI` | MongoDB connection string (default: `mongodb://localhost:27017/`) |
| `ORIGINS` | CORS allowed origins (default: `["*"]`) |
| `ALLOW_CREDENTIALS` | CORS allow credentials (default: `True`) |
| `ALLOWED_METHODS` | CORS allowed methods (default: `["*"]`) |
| `ALLOWED_HEADERS` | CORS allowed headers (default: `["*"]`) |

### Seed Dummy Data (for Chatbot tool-calling)
```bash
python scripts/setup_dummy_data.py
```
This inserts 4 dummy Daraz orders into `mongodb://localhost:27017/daraz.orders`.

### Running the Application

```bash
uvicorn main:app --reload
```

## API Base URL

- **Local Development**: `http://localhost:8000`
- **Remote Server**: `https://ai-features-ch9h.onrender.com`
- **Swagger UI**: `<BASE_URL>/docs`
- **ReDoc**: `<BASE_URL>/redoc`

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
- **Built-in tools**: `search_order(order_id)`, `get_recent_orders(limit)`
- **Success `data`**:
```json
{
  "message": "Your order ORD12345 has been shipped...",
  "session_id": "session_123"
}
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

## Technologies

| Technology | Purpose |
|---|---|
| FastAPI + Uvicorn | Web framework & ASGI server |
| LangGraph + LangChain | Chatbot agent, tool-calling, session memory |
| Google Gemini (`gemini-2.5-flash`) | LLM for chatbot |
| MongoDB + PyMongo | Order database for chatbot tools |
| PyMuPDF (`fitz`) | PDF text extraction |
| Ultralytics YOLO | Object detection model |
| OpenCV + NumPy | Image processing & annotation |
| Pydantic | Data validation |
| python-dotenv | Environment variable management |

## License

[Add your license here]
