# Lite-LLM-Chat Terminal

A sophisticated console application for interacting with the Lite-LLM-Chat backend. Features include multi-provider support, session management, real-time streaming, model switching, and beautiful terminal UI.

## Features

### Core Features
- **Multi-Provider Support**: Interact with different LLM providers (DeepSeek, etc.)
- **Session Management**: Create, load, save, and manage chat sessions
- **Real-Time Streaming**: Get responses in real-time as they're generated
- **Model Switching**: Switch between models anytime during a conversation
- **Thought Process Display**: See the model's reasoning when available
- **Auto-Save**: All messages are automatically saved to sessions
- **Beautiful UI**: Rich terminal interface with syntax highlighting and formatting

### Advanced Features
- **Command History**: Navigate previous commands with arrow keys
- **Auto-Suggestion**: Get suggestions based on command history
- **Temperature Control**: Adjust response creativity (0.0-2.0)
- **Session History**: Load and continue previous conversations
- **Metadata Display**: See which model generated each response

## Installation

### Prerequisites
- Python 3.8 or higher
- Backend server running on `http://localhost:8000` (default)

### Install Dependencies

```bash
cd terminal
pip install -r requirements.txt
```

The application requires:
- `aiohttp` - Async HTTP client for API communication
- `rich` - Beautiful terminal formatting and display
- `prompt_toolkit` - Advanced input handling and command history

## Usage

### Starting the Application

```bash
# Connect to default backend (http://localhost:8000)
python chat_console.py

# Connect to custom backend URL
python chat_console.py http://your-backend-url:port
```

### Basic Chat

Simply type your message and press Enter to chat:

```
> Hello, how are you?
```

The assistant will respond in real-time if streaming is enabled.

### Available Commands

#### Chat Commands
- Type your message - Send a chat message
- `/stop`, `/exit`, `/quit` - Exit the application
- `/clear` - Clear the screen
- `/help` - Show help information

#### Session Management
- `/new [title]` - Create a new chat session
  ```
  > /new My Research Session
  ```
- `/sessions` - List all available sessions
- `/load <session_id>` - Load an existing session
  ```
  > /load 5
  ```
- `/delete <session_id>` - Delete a session
  ```
  > /delete 3
  ```
- `/rename <new_title>` - Rename the current session
  ```
  > /rename Updated Title
  ```

#### Model Management
- `/providers` - List all available LLM providers
- `/models [provider]` - List available models
  ```
  > /models deepseek
  ```
- `/switch <provider> <model>` - Switch to a different model
  ```
  > /switch deepseek deepseek-reasoner
  ```

#### Settings
- `/stream on|off` - Toggle streaming mode
  ```
  > /stream off
  ```
- `/temp <0.0-2.0>` - Set temperature for responses
  ```
  > /temp 0.9
  ```
- `/info` - Show current session and settings information

## Configuration

### Backend URL
By default, the application connects to `http://localhost:8000`. You can change this by:

1. **Command line argument**:
   ```bash
   python chat_console.py http://192.168.1.100:8000
   ```

2. **Edit the script** (for permanent change):
   Modify the `backend_url` default in `chat_console.py`

### Default Settings
- **Streaming**: Enabled by default
- **Temperature**: 0.7 (balanced creativity)
- **Provider**: First available provider (usually DeepSeek)
- **Model**: First available model

## Examples

### Example 1: Quick Chat Session

```bash
$ python chat_console.py

> Hello!
🤖 Assistant: Hello! How can I help you today?

> What is Python?
🤖 Assistant: Python is a high-level, interpreted programming language...

> /exit
```

### Example 2: Working with Sessions

```bash
$ python chat_console.py

> /new Python Learning
✓ Created new session: Python Learning

> Explain list comprehensions
🤖 Assistant: List comprehensions provide a concise way...

> /sessions
# Shows all sessions including "Python Learning"

> /load 5
✓ Loaded session: Previous Chat
# Continues previous conversation

> /switch deepseek deepseek-reasoner
✓ Switched to deepseek/deepseek-reasoner
# Next messages use the new model
```

### Example 3: Model Comparison

```bash
> /new Model Comparison

> /switch deepseek deepseek-chat
✓ Switched to deepseek/deepseek-chat

> Explain quantum computing
🤖 Assistant: [Response from deepseek-chat]

> /switch deepseek deepseek-reasoner
✓ Switched to deepseek/deepseek-reasoner

> Explain quantum computing
🤖 Assistant: [Response from deepseek-reasoner]
🧠 Thinking: [Reasoning process if available]
```

## Architecture

The application is composed of three main modules:

### api_client.py (271 lines)
- Handles all HTTP communication with backend
- Provides async API for chat, sessions, models
- Manages streaming and non-streaming responses
- Data classes for Provider, Model, Session, Message

### ui_components.py (238 lines)
- Rich terminal UI components
- Formatted message display
- Tables for providers, models, sessions
- Color-coded output by message role
- Thinking process visualization

### chat_console.py (462 lines)
- Main application logic
- Command parser and handler
- Session state management
- Input handling with history
- Async event loop management

**Total**: ~971 lines (all under 500 lines per file)

## Keyboard Shortcuts

- **Arrow Up/Down** - Navigate command history
- **Ctrl+C** - Cancel current input (not exit)
- **Ctrl+D** or `/exit` - Exit application
- **Tab** - Auto-complete suggestions

## Troubleshooting

### Backend Connection Failed
```
✗ Backend not available at http://localhost:8000
ℹ Make sure the backend server is running
```
**Solution**: Start the backend server first
```bash
cd ../backend
uvicorn main:app --reload
```

### No Providers Available
```
✗ No providers or models available
```
**Solution**: Check backend configuration and API keys

### Session Not Found
```
✗ Session 5 not found
```
**Solution**: Use `/sessions` to see available sessions

## Tips and Best Practices

1. **Use Streaming**: Keep streaming enabled for better user experience
2. **Save Important Chats**: Use `/new` with descriptive titles
3. **Try Different Models**: Use `/switch` to compare model capabilities
4. **Adjust Temperature**: Lower (0.3-0.5) for factual, higher (0.8-1.2) for creative
5. **Check Session Info**: Use `/info` to verify current configuration
6. **Clean Up**: Delete old sessions with `/delete` to keep things organized

## Development

### Adding New Features
The modular architecture makes it easy to extend:

- **New commands**: Add handlers in `chat_console.py` `handle_command()` method
- **UI components**: Add methods to `ui_components.py` `ChatUI` class
- **API methods**: Add methods to `api_client.py` `APIClient` class

### Code Quality
- Type hints throughout for better IDE support
- Async/await for non-blocking I/O
- Error handling at all API boundaries
- Clean separation of concerns

## License

Part of the Lite-LLM-Chat project. See root LICENSE file.

## Support

For issues, questions, or contributions, please refer to the main project repository.
