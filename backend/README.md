# Lite-LLM-Chat Backend

FastAPI backend service with DeepSeek integration and SQLite database.

## Features

- ✅ FastAPI framework
- ✅ SQLite database for chat history
- ✅ DeepSeek API integration
- ✅ Streaming chat responses (SSE)
- ✅ Session management
- ✅ Multiple provider support (extensible)

## Installation

1. Install dependencies:
```bash
pip install -r requirement.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your DeepSeek API key
```

3. Run the server:
```bash
python main.py
```

The API will be available at <http://localhost:8000> with interactive docs at <http://localhost:8000/docs>.

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Providers

- `GET /api/v1/providers` - List available LLM providers

### Models

- `GET /api/v1/models` - List available models
- `GET /api/v1/models?provider=deepseek` - Filter models by provider

### Sessions

- `GET /api/v1/sessions` - List all chat sessions
- `GET /api/v1/sessions/{session_id}` - Get session details with messages
- `POST /api/v1/sessions` - Create a new session
- `PATCH /api/v1/sessions/{session_id}` - Update session
- `DELETE /api/v1/sessions/{session_id}` - Delete session

### Chat

- `POST /api/v1/chat` - Chat completion (streaming or non-streaming)

#### Chat Request Example (Streaming):

```json
{
  "session_id": 1,
  "provider": "deepseek",
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": true,
  "temperature": 0.7
}
```

#### Chat Request Example (New Session):

```json
{
  "provider": "deepseek",
  "model": "deepseek-chat",
  "title": "My Chat",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": true
}
```

### Health

- `GET /health` - Health check

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### ChatSession
- id (Primary Key)
- title
- provider
- model
- created_at
- updated_at

### ChatMessage
- id (Primary Key)
- session_id (Foreign Key)
- role (user/assistant/system)
- content
- created_at

## Architecture

```
backend/
├── main.py              # FastAPI application & routes
├── config.py            # Configuration settings
├── database.py          # SQLAlchemy models & DB setup
├── models.py            # Pydantic schemas
├── deepseek_client.py   # DeepSeek API client
├── requirement.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEEPSEEK_API_KEY | Your DeepSeek API key | None |
| DEEPSEEK_BASE_URL | DeepSeek API base URL | https://api.deepseek.com |
| DATABASE_URL | SQLite database path | sqlite:///./chat_history.db |
| APP_NAME | Application name | Lite-LLM-Chat Backend |
| APP_VERSION | Application version | 1.0.0 |

## Streaming Response Format

The streaming endpoint uses Server-Sent Events (SSE) format:

```
data: {"session_id": 1}

data: {"content": "Hello"}

data: {"content": " there"}

data: {"done": true}
```

## Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 201: Created
- 204: No Content
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
