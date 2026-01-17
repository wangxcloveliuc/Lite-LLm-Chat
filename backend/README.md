# Lite-LLM-Chat Backend

FastAPI backend service with multi-provider LLM integration and SQLite database.

## Features

- ✅ FastAPI framework with async support
- ✅ SQLite database for chat history
- ✅ **10 LLM Provider Support**: DeepSeek, Doubao, SiliconFlow, Groq, Mistral, Grok, OpenRouter, Gemini, Cerebras, and Nvidia
- ✅ Streaming chat responses (Server-Sent Events)
- ✅ Session management with CRUD operations
- ✅ Multi-modal content support (images, videos, audios)
- ✅ File upload functionality for media content
- ✅ Reasoning/thinking content support for inference models
- ✅ Model caching with configurable TTL
- ✅ Extensible provider architecture
- ✅ CORS support for frontend integration

## Supported LLM Providers

| Provider | Description | API Type |
|----------|-------------|----------|
| DeepSeek | DeepSeek AI language models | Custom |
| Doubao | Volcengine Ark language models | Custom |
| SiliconFlow | OpenAI-compatible models | OpenAI-compatible |
| Groq | Fast inference models | OpenAI-compatible |
| Mistral | Mistral AI models | OpenAI-compatible |
| Grok | xAI models | OpenAI-compatible |
| OpenRouter | Multi-provider routing | OpenAI-compatible |
| Gemini | Google Gemini models | Google GenAI SDK |
| Cerebras | Fast inference models | OpenAI-compatible |
| Nvidia | NIM models | OpenAI-compatible |

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys for the providers you want to use
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

### Health

- `GET /health` - Health check endpoint

### Providers

- `GET /api/v1/providers` - List available LLM providers

### Models

- `GET /api/v1/models` - List all available models
- `GET /api/v1/models?provider=deepseek` - Filter models by provider

### Sessions

- `GET /api/v1/sessions` - List all chat sessions (with pagination)
- `GET /api/v1/sessions/{session_id}` - Get session details with messages
- `POST /api/v1/sessions` - Create a new session
- `PATCH /api/v1/sessions/{session_id}` - Update session title
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `DELETE /api/v1/sessions/{session_id}/truncate/{message_id}` - Truncate session from message
- `DELETE /api/v1/sessions` - Delete all sessions

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

#### Chat Request Example (Multi-modal):

```json
{
  "provider": "gemini",
  "model": "gemini-2.0-flash-exp",
  "messages": [
    {
      "role": "user",
      "content": "What do you see in this image?",
      "images": ["/uploads/image.jpg"]
    }
  ],
  "stream": true,
  "image_detail": "high"
}
```

### Upload

- `POST /api/v1/upload` - Upload a file (image) and return its URL

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### ChatSession
- `id` (Primary Key) - Session identifier
- `title` - Session title
- `provider` - LLM provider used
- `model` - Model used
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### ChatMessage
- `id` (Primary Key) - Message identifier
- `session_id` (Foreign Key) - Associated session
- `role` - Message role (user/assistant/system)
- `content` - Message content
- `images` - List of image URLs/paths (JSON)
- `videos` - List of video URLs/paths (JSON)
- `audios` - List of audio URLs/paths (JSON)
- `thought_process` - Reasoning/thinking content from inference models
- `thought_signatures` - Thought signatures (JSON)
- `search_results` - Search results (JSON)
- `provider` - LLM provider used for this message
- `model` - Model used for this message
- `created_at` - Creation timestamp

## Architecture

```
backend/
├── main.py              # Application entry point
├── app_factory.py       # FastAPI app factory with middleware setup
├── config.py            # Configuration settings (pydantic-settings)
├── database.py          # SQLAlchemy models & DB setup
├── models.py            # Pydantic schemas for request/response
├── provider_registry.py # Provider discovery and model caching
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md           # This file
├── providers/          # LLM provider implementations
│   ├── __init__.py
│   ├── base.py         # Abstract base classes for providers
│   ├── openai_base.py  # OpenAI-compatible client base
│   ├── deepseek.py     # DeepSeek provider
│   ├── deepseek_client.py
│   ├── doubao.py       # Doubao provider
│   ├── doubao_client.py
│   ├── siliconflow.py  # SiliconFlow provider
│   ├── siliconflow_client.py
│   ├── groq.py         # Groq provider
│   ├── groq_client.py
│   ├── mistral.py      # Mistral provider
│   ├── mistral_client.py
│   ├── grok.py         # Grok provider
│   ├── grok_client.py
│   ├── openrouter.py   # OpenRouter provider
│   ├── openrouter_client.py
│   ├── gemini.py       # Gemini provider
│   ├── gemini_client.py
│   ├── gemini_config.py
│   ├── gemini_media.py
│   ├── gemini_messages.py
│   ├── gemini_response.py
│   ├── cerebras.py     # Cerebras provider
│   ├── cerebras_client.py
│   ├── nvidia.py       # Nvidia provider
│   └── nvidia_client.py
└── routers/            # API route handlers
    ├── __init__.py
    ├── chat.py         # Chat completion endpoint
    ├── chat_helpers.py # Helper functions for chat processing
    ├── sessions.py     # Session management endpoints
    ├── providers.py    # Provider listing endpoint
    ├── models.py       # Model listing endpoint
    ├── health.py       # Health check endpoint
    └── upload.py       # File upload endpoint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| **Application** | | |
| APP_NAME | Application name | Lite-LLM-Chat Backend |
| APP_VERSION | Application version | 1.0.0 |
| API_PREFIX | API URL prefix | /api/v1 |
| BACKEND_PORT | Server port | 8000 |
| **Database** | | |
| DATABASE_URL | SQLite database path | sqlite:///./chat_history.db |
| **DeepSeek** | | |
| DEEPSEEK_API_KEY | DeepSeek API key | None |
| DEEPSEEK_BASE_URL | DeepSeek API base URL | https://api.deepseek.com |
| **Doubao** | | |
| DOUBAO_API_KEY | Doubao API key | None |
| DOUBAO_BASE_URL | Doubao API base URL | https://ark.cn-beijing.volces.com/api/v3 |
| **SiliconFlow** | | |
| SILICONFLOW_API_KEY | SiliconFlow API key | None |
| SILICONFLOW_BASE_URL | SiliconFlow API base URL | https://api.siliconflow.cn/v1 |
| **Groq** | | |
| GROQ_API_KEY | Groq API key | None |
| GROQ_BASE_URL | Groq API base URL | https://api.groq.com/openai/v1 |
| **Mistral** | | |
| MISTRAL_API_KEY | Mistral API key | None |
| MISTRAL_BASE_URL | Mistral API base URL | https://api.mistral.ai/v1 |
| **Grok** | | |
| GROK_API_KEY | Grok API key | None |
| GROK_BASE_URL | Grok API base URL | https://api.x.ai/v1 |
| **OpenRouter** | | |
| OPENROUTER_API_KEY | OpenRouter API key | None |
| OPENROUTER_BASE_URL | OpenRouter API base URL | https://openrouter.ai/api/v1 |
| OPENROUTER_HTTP_REFERER | HTTP referer for attribution | None |
| OPENROUTER_X_TITLE | X-Title header for attribution | None |
| **Gemini** | | |
| GEMINI_API_KEY | Gemini API key | None |
| **Cerebras** | | |
| CEREBRAS_API_KEY | Cerebras API key | None |
| CEREBRAS_BASE_URL | Cerebras API base URL | https://api.cerebras.ai/v1 |
| **Nvidia** | | |
| NVIDIA_API_KEY | Nvidia API key | None |
| NVIDIA_BASE_URL | Nvidia API base URL | https://integrate.api.nvidia.com/v1 |
| **Network** | | |
| HTTP_PROXY | HTTP proxy for outbound requests | None |
| PROVIDER_TIMEOUT | Provider request timeout (seconds) | 20.0 |
| **Caching** | | |
| MODEL_CACHE_TTL | Model list cache TTL (seconds, 0 to disable) | 3600 |
| **CORS** | | |
| CORS_ORIGINS | Allowed CORS origins | [*] |

## Streaming Response Format

The streaming endpoint uses Server-Sent Events (SSE) format:

```
data: {"session_id": 1}

data: {"content": "Hello"}

data: {"content": " there"}

data: {"reasoning": "Thinking..."}

data: {"done": true}
```

### SSE Event Types

| Event | Description |
|-------|-------------|
| `session_id` | Session ID for new or existing session |
| `content` | Chat content chunk |
| `reasoning` | Reasoning/thinking content chunk |
| `search_results` | Search results from provider |
| `error` | Error message |
| `done` | Stream completion marker |

## Chat Request Parameters

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| session_id | int | None | Existing session ID (creates new if not provided) |
| provider | string | Required | LLM provider ID |
| model | string | Required | Model ID |
| messages | array | Required | Array of message objects |
| stream | boolean | true | Enable streaming response |
| temperature | float | 1.0 | Sampling temperature (0.0-2.0) |
| max_tokens | int | None | Maximum tokens to generate |
| max_completion_tokens | int | None | Maximum completion tokens |
| frequency_penalty | float | 0.0 | Frequency penalty (-2.0 to 2.0) |
| presence_penalty | float | 0.0 | Presence penalty (-2.0 to 2.0) |
| top_p | float | 1.0 | Nucleus sampling (0.0-1.0) |
| stop | array | None | Stop sequences |
| title | string | None | Session title (for new sessions) |
| system_prompt | string | None | System prompt override |

### Vision Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image_detail | string | None | Image detail level (auto/low/high) |
| image_pixel_limit | object | None | Image pixel limit settings |
| video_detail | string | None | Video detail level (auto/low/high) |
| max_frames | int | None | Maximum frames to process |
| fps | float | None | Frames per second for video |

### Provider-Specific Parameters

#### DeepSeek
- `thinking` (boolean) - Enable thinking mode
- `reasoning_effort` (string) - Reasoning effort level

#### SiliconFlow
- `enable_thinking` (boolean) - Enable thinking mode
- `thinking_budget` (int) - Thinking token budget (128-32768)
- `min_p` (float) - Min-p sampling (0.0-1.0)
- `top_k` (float) - Top-k sampling

#### OpenRouter
- `transforms` (array) - Response transformations
- `models` (array) - Model routing options
- `route` (string) - Routing strategy
- `repetition_penalty` (float) - Repetition penalty (0.0-2.0)
- `top_a` (float) - Top-a sampling (0.0-1.0)
- `logprobs` (boolean) - Enable log probabilities
- `top_logprobs` (int) - Top log probabilities (0-20)
- `response_format` (object) - Response format specification
- `structured_outputs` (boolean) - Enable structured outputs
- `parallel_tool_calls` (boolean) - Enable parallel tool calls
- `reasoning` (object) - Reasoning configuration
- `modalities` (array) - Content modalities
- `image_config` (object) - Image generation config
- `plugins` (array) - Plugin configuration
- `web_search_options` (object) - Web search options

#### Mistral
- `safe_prompt` (boolean) - Enable safe prompt mode
- `random_seed` (int) - Random seed for reproducibility

#### Gemini
- `thinking_level` (string) - Thinking level (minimal/low/medium/high)
- `media_resolution` (string) - Media resolution
- `google_search` (boolean) - Enable Google Search
- `url_context` (boolean) - Enable URL context
- `imagen_number_of_images` (int) - Number of images (1-4)
- `imagen_image_size` (string) - Image size (1K/2K)
- `imagen_aspect_ratio` (string) - Aspect ratio (1:1/3:4/4:3/9:16/16:9)
- `imagen_person_generation` (string) - Person generation policy

#### Doubao Seedream (Image Generation)
- `sequential_image_generation` (string) - Sequential generation mode
- `max_images` (int) - Maximum images
- `watermark` (boolean) - Add watermark
- `prompt_optimize_mode` (string) - Prompt optimization mode
- `size` (string) - Image size
- `seed` (int) - Random seed

#### Doubao Seedance (Video Generation)
- `resolution` (string) - Video resolution
- `ratio` (string) - Aspect ratio
- `duration` (int) - Video duration
- `generate_audio` (boolean) - Generate audio
- `draft` (boolean) - Draft mode
- `camera_fixed` (boolean) - Fixed camera

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Adding a New Provider

To add a new LLM provider:

1. Create a new provider module in `providers/` directory
2. Implement the `LLMProvider` or `BaseLLMProvider` class
3. Create a client class that implements the required methods
4. Add the provider to `providers/__init__.py`
5. Add configuration variables to `config.py`
6. Add API key configuration to `.env.example`

Example provider structure:

```python
from .base import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    id = "myprovider"
    name = "My Provider"
    description = "My custom LLM provider"
    supported = True

    def __init__(self):
        from .myprovider_client import myprovider_client
        super().__init__(myprovider_client)

    def _get_fallback_models(self) -> List[str]:
        return ["model-1", "model-2"]

provider = MyProvider()
```

## Development

### Running with Auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Initialization

The database is automatically initialized on startup. Tables are created using SQLAlchemy's `create_all()` method, and lightweight migrations are applied for existing databases.

### Testing

Use the interactive API documentation at `/docs` to test endpoints.

## License

See the main project LICENSE file.
