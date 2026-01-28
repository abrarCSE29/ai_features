# AI Features API

A modular FastAPI application for implementing various AI features with clean separation of concerns.

## Project Overview

This project implements AI-powered services using a modular architecture. Each feature is organized as an independent module, making the codebase scalable, maintainable, and easy to extend.

## Architecture

- **Modular Design**: Each AI feature (e.g., OCR, Chatbot) is implemented as a separate module
- **Router-based Organization**: Each module has its own router for endpoint management
- **Service Layer**: Business logic is separated into dedicated service classes
- **Pydantic Models**: Strong typing with request/response validation

## Current Features

### OCR (Optical Character Recognition)
Extract text from PDF documents using PyMuPDF. The OCR module provides text extraction capabilities for document processing.

## Project Structure (at present)

```
ai_features/
├── config/
│   └── app_config.py          # Configuration management
├── modules/
│   ├── chatbot/               # Chatbot module (coming soon)
│   │   └── chatbot_service.py
│   └── ocr/                   # OCR module
│       ├── __init__.py
│       ├── router.py          # API endpoints
│       ├── models.py          # Pydantic response models
│       ├── service.py         # OCR service logic
│       └── tests/
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

### Running the Application

Start the API server:
```bash
uvicorn main:app --reload
```

## API Base URL

Replace `<BASE_URL>` with your server URL:
- **Local Development**: `http://localhost:8000`
- **Remote Server**: `https://ai-features-ch9h.onrender.com` 
- **API Documentation**: `<BASE_URL>/docs` (Swagger UI)
- **Alternative Documentation**: `<BASE_URL>/redoc` (ReDoc)

## API Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Full URL**: `<BASE_URL>/health`
- **Description**: Check if the API is running
- **Response**:
```json
{
  "status": "ai api running"
}
```

### OCR - Extract Text from PDF

- **Endpoint**: `POST /ocr/extract-text`
- **Full URL**: `<BASE_URL>/ocr/extract-text`
- **Description**: Extract text from an uploaded PDF file
- **Parameters**:
  - `file` (form-data, required): PDF file to extract text from
- **Success Response** (200):
```json
{
  "status": "success",
  "filename": "document.pdf",
  "text": "Extracted text from the PDF..."
}
```
- **Error Response**:
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Interactive API Documentation

Use the Swagger UI or ReDoc for interactive endpoint testing:
- **Swagger UI**: `<BASE_URL>/docs`
- **ReDoc**: `<BASE_URL>/redoc`

## Technologies

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation and settings management
- **PyMuPDF**: PDF text extraction
- **Python 3.10+**: Programming language

## Dependencies

See `requirements.txt` for all project dependencies. Key dependencies include:
- fastapi
- uvicorn
- pydantic
- python-multipart
- PyMuPDF

## Future Enhancements

- Chatbot module implementation
- Additional AI features
- Enhanced error handling and logging
- Unit and integration tests
- Database integration

## License

[Add your license here]
