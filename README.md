# AI Features API

A modular FastAPI application for implementing various AI features with clean separation of concerns.

## Project Overview

This project implements AI-powered services using a modular architecture. Each feature is organized as an independent module, making the codebase scalable, maintainable, and easy to extend.

## Architecture

- **Modular Design**: Each AI feature (e.g., OCR, Chatbot) is implemented as a separate module.
- **Router-based Organization**: Each module has its own router for endpoint management.
- **Service Layer**: Business logic is separated into dedicated service classes.
- **Pydantic Models**: Strong typing with request/response validation.
- **Agentic AI**: The chatbot uses LangGraph and Google Gemini for tool-calling capabilities.

## Current Features

### OCR (Optical Character Recognition)
Extract text from PDF documents using PyMuPDF. The OCR module provides text extraction capabilities for document processing.

### Chatbot (Order Tracking Assistant)
An intelligent assistant for Daraz, an e-commerce platform.
- **Order Tracking**: Users can check their order status by providing an order ID.
- **Recent Orders**: Users can view their latest orders.
- **Memory**: Supports per-session conversation history using LangGraph's `MemorySaver`.
- **Tool Calling**: Uses ReAct agent pattern to interact with a MongoDB database.

## Project Structure

```
ai_features/
├── config/
│   └── app_config.py          # Configuration management
├── modules/
│   ├── chatbot/               # Chatbot module
│   │   ├── tests/             # Module-specific tests
│   │   ├── chatbot_service.py # Core chatbot logic (LangGraph/Gemini)
│   │   ├── models.py          # Pydantic models for chatbot
│   │   ├── router.py          # API endpoints
│   │   └── tools.py           # LangChain tools for DB interaction
│   └── ocr/                   # OCR module
│       ├── tests/
│       ├── models.py
│       ├── router.py
│       └── service.py
├── scripts/
│   └── setup_dummy_data.py    # Script to populate MongoDB with test data
├── utils/
│   └── api_response/          # Standardized API response utilities
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Project dependencies
└── README.md                  # This file
```

## Setup

### Installation

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

### Environment Configuration

Create a `.env` file in the root directory and add the following:

```env
# AI Features
GOOGLE_API_KEY=your_google_api_key_here

# Database
MONGO_URI=mongodb://localhost:27017/
```

### Database Setup

To populate your MongoDB with dummy order data for the chatbot:
```bash
python scripts/setup_dummy_data.py
```

### Running the Application

Start the API server:
```bash
uvicorn main:app --reload
```

## API Base URL

- **Local Development**: `http://localhost:8000`
- **Remote Server**: `https://ai-features-ch9h.onrender.com` 
- **API Documentation**: `<BASE_URL>/docs` (Swagger UI)
- **Alternative Documentation**: `<BASE_URL>/redoc` (ReDoc)

## API Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Description**: Check if the API is running
- **Response**:
```json
{
  "status": "ai api running"
}
```

### OCR - Extract Text from PDF

- **Endpoint**: `POST /ocr/extract-text`
- **Description**: Extract text from an uploaded PDF file
- **Parameters**:
  - `file` (form-data, required): PDF file to extract text from
- **Success Response** (200):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Text extracted successfully",
  "data": {
    "filename": "document.pdf",
    "text": "Extracted text from the PDF..."
  }
}
```

### Chatbot - Interact with Bot

- **Endpoint**: `POST /chatbot/chat`
- **Description**: Send a message to the AI assistant for order tracking and general queries.
- **Request Body**:
```json
{
  "message": "Where is my order ORD12345?",
  "session_id": "session_123"
}
```
- **Success Response** (200):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Response generated successfully",
  "data": {
    "bot_response": "Your order ORD12345 has been shipped and is expected to arrive on 2023-12-01.",
    "session_id": "session_123"
  }
}
```

## Technologies

- **FastAPI**: Web framework for building APIs.
- **LangChain / LangGraph**: Framework for building LLM-powered agents.
- **Google Gemini**: Generative AI model for natural language processing.
- **MongoDB**: NoSQL database for order data storage.
- **PyMuPDF**: PDF text extraction.
- **Pydantic**: Data validation and settings management.

## Dependencies

Key dependencies include:
- `fastapi`
- `langchain-google-genai`
- `langgraph`
- `pymongo`
- `pymupdf`
- `python-dotenv`

## License

[Add your license here]
