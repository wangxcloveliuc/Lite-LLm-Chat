# Lite-LLM-Chat

A modern, multi-provider LLM chat application with support for 10 different AI providers, featuring real-time streaming responses, multi-modal content support, and a clean, responsive interface.

## Features

- ✅ **10 LLM Provider Support**: DeepSeek, Doubao, SiliconFlow, Groq, Mistral, Grok, OpenRouter, Gemini, Cerebras, and Nvidia
- ✅ **Real-time Streaming**: Server-Sent Events (SSE) for instant response streaming
- ✅ **Multi-modal Support**: Upload and chat with images, videos, and audio files
- ✅ **Session Management**: Create, rename, delete, and truncate chat sessions
- ✅ **Message Editing**: Edit user messages and regenerate assistant responses
- ✅ **Reasoning Display**: View thought processes from inference models
- ✅ **Search Results**: Display web search results from supported providers
- ✅ **Provider-specific Settings**: Fine-tune parameters for each provider
- ✅ **Vision Settings**: Configure image and video processing options
- ✅ **Markdown Rendering**: Rich text formatting with syntax highlighting
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **TypeScript**: Full type safety across the entire codebase

## Architecture

```
Lite-LLM-Chat/
├── backend/                 # FastAPI backend service
│   ├── providers/          # LLM provider implementations
│   ├── routers/            # API route handlers
│   ├── models.py           # Pydantic schemas
│   ├── database.py         # SQLAlchemy models
│   ├── config.py           # Configuration settings
│   ├── main.py             # Application entry point
│   └── README.md           # Backend documentation
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── api/            # API client
│   │   ├── styles/         # CSS modules
│   │   └── types.ts        # TypeScript types
│   ├── public/             # Static assets
│   └── README.md           # Frontend documentation
├── terminal/               # Terminal-based chat client
│   ├── api_client.py       # API client
│   ├── chat_console.py     # Console interface
│   └── README.md           # Terminal documentation
├── start_backend.bat       # Windows: Start backend server
├── start_frontend.bat      # Windows: Start frontend dev server
├── LICENSE                 # License file
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Lite-LLm-Chat
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
cp .env.example .env
# Edit .env and set your backend URL
```

### Running the Application

#### Windows (Batch Files)
```bash
# Terminal 1: Start backend
start_backend.bat

# Terminal 2: Start frontend
start_frontend.bat
```

#### Manual Start

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Supported LLM Providers

| Provider | Description | API Type |
|----------|-------------|----------|
| [DeepSeek](https://www.deepseek.com/) | DeepSeek AI language models | Custom |
| [Doubao](https://www.volcengine.com/) | Volcengine Ark language models | Custom |
| [SiliconFlow](https://siliconflow.cn/) | OpenAI-compatible models | OpenAI-compatible |
| [Groq](https://groq.com/) | Fast inference models | OpenAI-compatible |
| [Mistral](https://mistral.ai/) | Mistral AI models | OpenAI-compatible |
| [Grok](https://x.ai/) | xAI models | OpenAI-compatible |
| [OpenRouter](https://openrouter.ai/) | Multi-provider routing | OpenAI-compatible |
| [Gemini](https://ai.google.dev/) | Google Gemini models | Google GenAI SDK |
| [Cerebras](https://www.cerebras.ai/) | Fast inference models | OpenAI-compatible |
| [Nvidia](https://build.nvidia.com/) | NIM models | OpenAI-compatible |

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Doubao
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# SiliconFlow
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Mistral
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_BASE_URL=https://api.mistral.ai/v1

# Grok
GROK_API_KEY=your_grok_api_key_here
GROK_BASE_URL=https://api.x.ai/v1

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Cerebras
CEREBRAS_API_KEY=your_cerebras_api_key_here
CEREBRAS_BASE_URL=https://api.cerebras.ai/v1

# Nvidia
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# Database
DATABASE_URL=sqlite:///./chat_history.db

# Server
BACKEND_PORT=8000
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_PORT=5173
VITE_BACKEND_URL=http://localhost:8000
```

## API Endpoints

### Health
- `GET /health` - Health check

### Providers
- `GET /api/v1/providers` - List available LLM providers

### Models
- `GET /api/v1/models` - List all available models
- `GET /api/v1/models?provider=deepseek` - Filter models by provider

### Sessions
- `GET /api/v1/sessions` - List all chat sessions
- `GET /api/v1/sessions/{session_id}` - Get session details with messages
- `POST /api/v1/sessions` - Create a new session
- `PATCH /api/v1/sessions/{session_id}` - Update session title
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `DELETE /api/v1/sessions/{session_id}/truncate/{message_id}` - Truncate session from message
- `DELETE /api/v1/sessions` - Delete all sessions

### Chat
- `POST /api/v1/chat` - Chat completion (streaming or non-streaming)

### Upload
- `POST /api/v1/upload` - Upload a file (image, video, or audio)

## Documentation

- [Backend Documentation](backend/README.md) - Detailed backend API documentation
- [Frontend Documentation](frontend/README.md) - Frontend architecture and components
- [Terminal Documentation](terminal/README.md) - Terminal-based chat client

## Features in Detail

### Streaming Responses
The application uses Server-Sent Events (SSE) for real-time streaming of chat responses, providing instant feedback as the AI generates its response.

### Multi-modal Support
Users can upload images, videos, and audio files to include in their conversations. The frontend handles file uploads with progress tracking and displays media content inline.

### Session Management
- Create new chat sessions
- Rename sessions
- Delete individual sessions
- Truncate sessions from a specific message
- Delete all sessions

### Message Operations
- Edit user messages (truncates and regenerates)
- Regenerate assistant responses
- Copy message content
- View thought processes from reasoning models

### Provider-specific Settings
Each provider has its own set of configurable parameters:
- Common settings (temperature, max tokens, top P, etc.)
- Vision settings (image detail, video FPS, etc.)
- Provider-specific options (thinking mode, reasoning effort, etc.)

### Search Results
Providers that support web search (like Gemini with Google Search) display search results with links to sources.

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Embedded database
- **OpenAI SDK** - For OpenAI-compatible providers
- **Google GenAI SDK** - For Gemini provider
- **Volcengine SDK** - For Doubao provider

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **react-markdown** - Markdown rendering
- **react-syntax-highlighter** - Code syntax highlighting
- **remark-gfm** - GitHub Flavored Markdown
- **remark-breaks** - Line break handling

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend will be available at http://localhost:8000 with interactive API documentation at http://localhost:8000/docs.

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173.

### Building for Production

**Backend:**
```bash
cd backend
# No build step required, just run with production settings
python main.py
```

**Frontend:**
```bash
cd frontend
npm run build
npm run preview
```

## Terminal Client

A terminal-based chat client is included for users who prefer command-line interfaces.

```bash
cd terminal
pip install -r requirements.txt
python chat_console.py
```

See [terminal/README.md](terminal/README.md) for more details.

## Browser Support

The frontend supports modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.
