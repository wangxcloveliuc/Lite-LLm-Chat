# Lite-LLM-Chat Frontend

React + TypeScript + Vite frontend for the Lite-LLM-Chat application with multi-provider LLM support.

## Features

- ✅ React 19 with TypeScript
- ✅ Vite for fast development and optimized builds
- ✅ **10 LLM Provider Support**: DeepSeek, Doubao, SiliconFlow, Groq, Mistral, Grok, OpenRouter, Gemini, Cerebras, and Nvidia
- ✅ Real-time streaming chat responses (Server-Sent Events)
- ✅ Multi-modal content support (images, videos, audios)
- ✅ File upload with progress tracking
- ✅ Session management (create, rename, delete, truncate)
- ✅ Message editing and regeneration
- ✅ Markdown rendering with syntax highlighting
- ✅ Thought process/reasoning display for inference models
- ✅ Search results display
- ✅ Provider-specific settings
- ✅ Vision settings for image/video processing
- ✅ Responsive design
- ✅ Image lightbox for viewing attachments

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| TypeScript | 5.9.3 | Type safety |
| Vite | 7.2.4 | Build tool & dev server |
| react-markdown | 10.1.0 | Markdown rendering |
| react-syntax-highlighter | 16.1.0 | Code syntax highlighting |
| remark-gfm | 4.0.1 | GitHub Flavored Markdown |
| remark-breaks | 4.0.0 | Line break handling |

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and set your backend URL
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at <http://localhost:5173> (or the port specified in `VITE_PORT`).

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_PORT | Development server port | 5173 |
| VITE_BACKEND_URL | Backend API URL | http://localhost:8000 |

### Example `.env` file

```env
VITE_PORT=5173
VITE_BACKEND_URL=http://localhost:8000
```

## Development

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Architecture

```
frontend/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Root component
│   ├── App.css               # Global styles
│   ├── index.css             # Base styles
│   ├── types.ts              # TypeScript type definitions
│   ├── api/                  # API client
│   │   └── apiClient.ts      # Backend API client
│   ├── components/           # React components
│   │   ├── App.tsx           # Root component
│   │   ├── ChatArea.tsx      # Chat area container
│   │   ├── Header.tsx        # Header with provider/model selectors
│   │   ├── Sidebar.tsx       # Session list sidebar
│   │   ├── SettingsSidebar.tsx  # Settings panel
│   │   ├── chat/             # Chat-related components
│   │   │   ├── ChatInputBar.tsx    # Message input with file upload
│   │   │   ├── ChatLightbox.tsx    # Image lightbox
│   │   │   ├── ChatMessage.tsx     # Individual message component
│   │   │   ├── MessageList.tsx     # Message list container
│   │   │   └── utils.ts            # Utility functions
│   │   └── settingsSidebar/  # Settings components
│   │       ├── CommonSettingsSection.tsx      # Common settings
│   │       ├── VisionSettingsSection.tsx      # Vision settings
│   │       ├── ProviderSpecificSettings.tsx   # Provider-specific settings
│   │       ├── useSidebarDismiss.ts           # Sidebar dismiss hook
│   │       └── providerSpecific/              # Provider-specific sections
│   │           ├── CerebrasSettingsSection.tsx
│   │           ├── DoubaoSeedanceSettingsSection.tsx
│   │           ├── DoubaoSeedreamSettingsSection.tsx
│   │           ├── DoubaoSettingsSection.tsx
│   │           ├── GeminiImageGenerationSettingsSection.tsx
│   │           ├── GeminiImagenSettingsSection.tsx
│   │           ├── GeminiSettingsSection.tsx
│   │           ├── GrokSettingsSection.tsx
│   │           ├── GroqSettingsSection.tsx
│   │           ├── MistralSettingsSection.tsx
│   │           ├── NvidiaSettingsSection.tsx
│   │           ├── OpenRouterSettingsSection.tsx
│   │           └── SiliconFlowSettingsSection.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useChatApp.ts     # Main app hook
│   │   ├── useChatMessages.ts # Message management
│   │   ├── useChatResources.ts # Resource management
│   │   ├── useChatSettings.ts # Settings management
│   │   └── useSettingsPanel.ts # Settings panel state
│   ├── styles/               # CSS modules
│   │   ├── base.css          # Base styles
│   │   ├── chat.css          # Chat styles
│   │   ├── chat-actions.css  # Chat action buttons
│   │   ├── context-menu.css  # Context menu styles
│   │   ├── focus.css         # Focus styles
│   │   ├── header.css        # Header styles
│   │   ├── input.css         # Input styles
│   │   ├── layout.css        # Layout styles
│   │   ├── markdown.css      # Markdown styles
│   │   ├── responsive.css    # Responsive styles
│   │   ├── settings-sidebar.css  # Settings sidebar styles
│   │   ├── sidebar-actions.css   # Sidebar action styles
│   │   └── sidebar.css       # Sidebar styles
│   └── assets/               # Static assets
├── public/                   # Public files
│   └── vite.svg             # Vite logo
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
├── tsconfig.app.json        # App TypeScript config
├── tsconfig.node.json       # Node TypeScript config
├── eslint.config.js         # ESLint configuration
└── .env.example             # Environment variables template
```

## Components

### Main Components

#### App
Root component that orchestrates all other components and manages global state.

#### ChatArea
Main chat interface containing the message list and input bar.

#### Header
Top bar with provider and model selectors, and settings button.

#### Sidebar
Left panel showing chat sessions with create, rename, and delete functionality.

#### SettingsSidebar
Right panel for configuring provider-specific and common settings.

### Chat Components

#### ChatInputBar
Message input component with:
- Text input with Enter to send
- File attachment button (images, videos, audios)
- Upload progress indicators
- Stop generation button

#### ChatMessage
Individual message component with:
- Markdown rendering with syntax highlighting
- Image/video/audio attachments
- Thought process display (collapsible)
- Search results display
- Copy, edit, and refresh actions

#### MessageList
Container for all messages with:
- Auto-scroll to latest message
- Typing indicator during generation

#### ChatLightbox
Image lightbox for viewing full-size images.

### Settings Components

#### CommonSettingsSection
Common settings for all providers:
- System prompt
- Temperature
- Max tokens
- Top P
- Frequency penalty
- Presence penalty
- Stop sequences

#### VisionSettingsSection
Vision-related settings:
- Image detail (auto/low/high)
- Image pixel limits
- Video FPS
- Video detail
- Max frames

#### ProviderSpecificSettings
Dynamic component that renders provider-specific settings based on the selected provider.

## Hooks

### useChatApp
Main hook that combines all other hooks and provides the complete app interface.

### useChatMessages
Manages message state and chat operations:
- Send messages with streaming support
- Stop generation
- Edit messages
- Refresh/regenerate responses
- Truncate sessions

### useChatResources
Manages app resources:
- Providers and models
- Sessions
- Current session state
- Provider/model selection

### useChatSettings
Manages settings for all providers:
- Provider-specific settings
- Common settings
- Vision settings
- Settings persistence

### useSettingsPanel
Manages settings panel state:
- Open/close
- Model refresh on provider change

## API Client

The `apiClient` provides methods for interacting with the backend API:

| Method | Description |
|--------|-------------|
| `healthCheck()` | Check backend health |
| `getProviders()` | Get available providers |
| `getModels(provider?)` | Get available models |
| `getSessions(skip?, limit?)` | Get chat sessions |
| `getSession(sessionId)` | Get session details |
| `createSession(title, provider, model)` | Create new session |
| `updateSession(sessionId, title)` | Update session title |
| `deleteSession(sessionId)` | Delete session |
| `deleteAllSessions()` | Delete all sessions |
| `truncateSession(sessionId, messageId)` | Truncate session from message |
| `uploadImage(file, onProgress?)` | Upload image |
| `uploadVideo(file, onProgress?)` | Upload video |
| `uploadAudio(file, onProgress?)` | Upload audio |
| `chatStream(request, signal?)` | Stream chat response |
| `chat(request)` | Non-streaming chat response |

## Types

### Core Types

```typescript
interface Provider {
  id: string;
  name: string;
  description: string;
  supported?: boolean;
}

interface Model {
  id: string;
  name: string;
  provider: string;
  description: string;
  context_length?: number;
}

interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  images?: string[];
  videos?: string[];
  audios?: string[];
  search_results?: SearchResult[];
  created_at?: string;
  provider?: string;
  model?: string;
  thought_process?: string;
  thought_signatures?: string[];
}

interface Session {
  id: number;
  title: string;
  provider: string;
  model: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: Message[];
}
```

### Settings Types

Each provider has its own settings interface:

- `DeepSeekSettings`
- `DoubaoSettings`
- `DoubaoSeedreamSettings` (image generation)
- `DoubaoSeedanceSettings` (video generation)
- `SiliconFlowSettings`
- `CerebrasSettings`
- `GroqSettings`
- `GrokSettings`
- `NvidiaSettings`
- `OpenRouterSettings`
- `GeminiSettings`
- `MistralSettings`

## Supported LLM Providers

| Provider | Description | Special Features |
|----------|-------------|------------------|
| DeepSeek | DeepSeek AI language models | Thinking mode, reasoning effort |
| Doubao | Volcengine Ark language models | Thinking mode, Seedream (image), Seedance (video) |
| SiliconFlow | OpenAI-compatible models | Thinking mode, thinking budget |
| Groq | Fast inference models | Reasoning format, include reasoning |
| Mistral | Mistral AI models | Safe prompt, random seed |
| Grok | xAI models | Standard settings |
| OpenRouter | Multi-provider routing | Extensive routing options, web search |
| Gemini | Google Gemini models | Google Search, Imagen (image generation) |
| Cerebras | Fast inference models | Reasoning effort |
| Nvidia | NIM models | Thinking mode |

## Settings

### Common Settings

Available for most providers:

| Setting | Type | Range | Description |
|---------|------|-------|-------------|
| System Prompt | string | - | Define assistant behavior |
| Temperature | float | 0.0-2.0 | Output randomness |
| Max Tokens | int | 1+ | Maximum tokens to generate |
| Top P | float | 0.0-1.0 | Nucleus sampling |
| Frequency Penalty | float | -2.0 to 2.0 | Penalize frequent tokens |
| Presence Penalty | float | -2.0 to 2.0 | Penalize new tokens |
| Stop Sequences | string | - | Comma-separated stop sequences |

### Vision Settings

Available for vision-capable models:

| Setting | Type | Range | Description |
|---------|------|-------|-------------|
| Image Detail | select | auto/low/high | Image processing detail |
| Image Pixel Limit | object | - | Max/min pixels |
| Video FPS | float | 0.1-10.0 | Video sampling rate |
| Video Detail | select | auto/low/high | Video processing detail |
| Max Frames | int | 1+ | Maximum frames to extract |

### Provider-Specific Settings

#### DeepSeek
- `thinking` (boolean) - Enable thinking mode
- `reasoning_effort` (low/medium/high) - Reasoning effort level

#### Doubao
- `thinking` (boolean) - Enable thinking mode
- `reasoning_effort` (low/medium/high) - Reasoning effort level
- `max_completion_tokens` (int) - Maximum completion tokens

#### Doubao Seedream (Image Generation)
- `size` (string) - Image size
- `seed` (int) - Random seed
- `sequential_image_generation` (auto/disabled) - Sequential generation
- `max_images` (int) - Maximum images
- `watermark` (boolean) - Add watermark
- `prompt_optimize_mode` (standard/fast) - Prompt optimization

#### Doubao Seedance (Video Generation)
- `resolution` (480p/720p/1080p) - Video resolution
- `ratio` (16:9/4:3/1:1/3:4/9:16/21:9/adaptive) - Aspect ratio
- `duration` (int) - Video duration
- `watermark` (boolean) - Add watermark
- `generate_audio` (boolean) - Generate audio
- `draft` (boolean) - Draft mode
- `seed` (int) - Random seed
- `camera_fixed` (boolean) - Fixed camera

#### SiliconFlow
- `enable_thinking` (boolean) - Enable thinking mode
- `thinking_budget` (int) - Thinking token budget (128-32768)
- `min_p` (float) - Min-p sampling (0.0-1.0)
- `top_k` (float) - Top-k sampling

#### Groq
- `reasoning_format` (parsed/raw/hidden) - Reasoning format
- `include_reasoning` (boolean) - Include reasoning
- `reasoning_effort` (none/default/low/medium/high) - Reasoning effort
- `max_completion_tokens` (int) - Maximum completion tokens

#### OpenRouter
- `transforms` (string) - Response transformations
- `models` (string) - Model routing options
- `route` (fallback/sort) - Routing strategy
- `include_reasoning` (boolean) - Include reasoning
- `repetition_penalty` (float) - Repetition penalty (0.0-2.0)
- `top_a` (float) - Top-a sampling (0.0-1.0)
- `logprobs` (boolean) - Enable log probabilities
- `top_logprobs` (int) - Top log probabilities (0-20)
- `response_format` (string) - Response format JSON
- `structured_outputs` (boolean) - Enable structured outputs
- `parallel_tool_calls` (boolean) - Enable parallel tool calls
- `reasoning_effort` (xhigh/high/medium/low/minimal/none) - Reasoning effort
- `reasoning_summary` (auto/concise/detailed) - Reasoning summary
- `image_generation` (boolean) - Enable image generation
- `image_aspect_ratio` (string) - Image aspect ratio
- `image_size` (1K/2K/4K) - Image size
- `web_search` (boolean) - Enable web search
- `web_search_results` (int) - Number of search results
- `web_search_engine` (native/exa) - Search engine
- `web_search_prompt` (string) - Search prompt
- `web_search_context_size` (low/medium/high) - Search context size

#### Gemini
- `top_k` (int) - Top-k sampling
- `seed` (int) - Random seed
- `thinking_budget` (int) - Thinking token budget
- `safety_threshold` (BLOCK_NONE/BLOCK_LOW_AND_ABOVE/BLOCK_MED_AND_ABOVE/BLOCK_ONLY_HIGH) - Safety threshold
- `thinking_level` (minimal/low/medium/high) - Thinking level
- `media_resolution` (MEDIA_RESOLUTION_UNSPECIFIED/MEDIA_RESOLUTION_LOW/MEDIA_RESOLUTION_MEDIUM/MEDIA_RESOLUTION_HIGH) - Media resolution
- `google_search` (boolean) - Enable Google Search
- `url_context` (boolean) - Enable URL context
- `response_modalities` (IMAGE/TEXT) - Response modalities
- `image_aspect_ratio` (string) - Image aspect ratio
- `image_size` (1K/2K/4K) - Image size
- `imagen_number_of_images` (1-4) - Number of images
- `imagen_image_size` (1K/2K) - Imagen image size
- `imagen_aspect_ratio` (1:1/3:4/4:3/9:16/16:9) - Imagen aspect ratio
- `imagen_person_generation` (dont_allow/allow_adult/allow_all) - Person generation policy

#### Mistral
- `safe_prompt` (boolean) - Enable safe prompt mode
- `random_seed` (int) - Random seed

#### Cerebras
- `reasoning_effort` (low/medium/high) - Reasoning effort
- `disable_reasoning` (boolean) - Disable reasoning

#### Nvidia
- `thinking` (boolean) - Enable thinking mode
- `reasoning_effort` (low/medium/high) - Reasoning effort

## Styling

The application uses modular CSS files organized by feature:

- `base.css` - Base styles and reset
- `layout.css` - Main layout structure
- `header.css` - Header component styles
- `sidebar.css` - Sidebar component styles
- `chat.css` - Chat area styles
- `chat-actions.css` - Chat action button styles
- `input.css` - Input component styles
- `markdown.css` - Markdown rendering styles
- `settings-sidebar.css` - Settings sidebar styles
- `context-menu.css` - Context menu styles
- `focus.css` - Focus state styles
- `responsive.css` - Responsive design styles

## Features in Detail

### Streaming Responses
The application uses Server-Sent Events (SSE) for real-time streaming of chat responses. The streaming is handled by the `chatStream` method in the API client.

### Multi-modal Support
Users can upload images, videos, and audio files which are sent to the backend and included in the chat request. Upload progress is displayed during the upload process.

### Message Editing
User messages can be edited. When edited, the session is truncated from that message and the conversation continues with the new content.

### Message Regeneration
Assistant responses can be regenerated. This truncates the session from the user's message and sends a new request.

### Thought Process Display
For inference models that support reasoning (like DeepSeek Reasoner), the thought process is displayed in a collapsible section.

### Search Results
When providers return search results (like Gemini with Google Search), they are displayed in a collapsible section with links to the sources.

### Session Management
- Create new sessions
- Rename sessions
- Delete sessions
- Truncate sessions from a specific message
- Delete all sessions

## Browser Support

The application supports modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

See the main project LICENSE file.
