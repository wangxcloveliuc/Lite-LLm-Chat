"""
Lite-LLM-Chat Terminal Console Application
Main application with session management, model switching, and streaming support
"""
import asyncio
import sys
from typing import Optional, List
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from api_client import APIClient, Message, Session, Provider, Model
from ui_components import ChatUI


class ChatConsole:
    """Main console application for chat interaction"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.client: Optional[APIClient] = None
        self.ui = ChatUI()
        
        # Session state
        self.current_session: Optional[Session] = None
        self.current_provider: str = "deepseek"
        self.current_model: str = "deepseek-chat"
        
        # Settings
        self.streaming_enabled: bool = True
        self.temperature: float = 0.7
        self.max_tokens: Optional[int] = None
        
        # Prompt session for input
        self.prompt_session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        # Available providers and models cache
        self.providers: List[Provider] = []
        self.models: List[Model] = []
    
    async def initialize(self):
        """Initialize the application"""
        self.client = APIClient(self.backend_url)
        await self.client.__aenter__()
        
        # Check backend health
        if not await self.client.health_check():
            self.ui.print_error(f"Backend not available at {self.backend_url}")
            self.ui.print_info("Make sure the backend server is running")
            return False
        
        # Load providers and models
        self.providers = await self.client.get_providers()
        self.models = await self.client.get_models()
        
        if not self.providers or not self.models:
            self.ui.print_error("No providers or models available")
            return False
        
        # Set default provider and model
        if self.models:
            self.current_provider = self.models[0].provider
            self.current_model = self.models[0].id
        
        return True
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    async def create_session(self, title: Optional[str] = None):
        """Create a new chat session"""
        if not title:
            title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = await self.client.create_session(
            title=title,
            provider=self.current_provider,
            model=self.current_model
        )
        
        if session:
            self.current_session = session
            self.ui.print_success(f"Created new session: {session.title}")
            return True
        else:
            self.ui.print_error("Failed to create session")
            return False
    
    async def load_session(self, session_id: int):
        """Load an existing session"""
        session = await self.client.get_session(session_id)
        
        if session:
            self.current_session = session
            self.current_provider = session.provider
            self.current_model = session.model
            self.ui.print_success(f"Loaded session: {session.title}")
            
            # Display session history
            if session.messages:
                self.ui.print_divider()
                for msg in session.messages:
                    self.ui.print_message(msg, show_metadata=True)
                self.ui.print_divider()
            
            return True
        else:
            self.ui.print_error(f"Session {session_id} not found")
            return False
    
    async def send_message(self, content: str):
        """Send a message and get response"""
        # Ensure we have a session
        if not self.current_session:
            if not await self.create_session():
                return
        
        # Create user message
        user_message = Message(role="user", content=content)
        
        # Display user message
        self.ui.print_message(user_message)
        
        # Prepare messages for API (only the new user message)
        messages = [user_message]
        
        try:
            if self.streaming_enabled:
                await self._handle_streaming_response(messages)
            else:
                await self._handle_non_streaming_response(messages)
        except Exception as e:
            self.ui.print_error(f"Error during chat: {str(e)}")
    
    async def _handle_streaming_response(self, messages: List[Message]):
        """Handle streaming chat response"""
        full_content = ""
        thinking_content = ""
        session_id = None
        has_error = False
        
        self.ui.print_streaming_start()
        
        async for chunk in self.client.chat_stream(
            messages=messages,
            provider=self.current_provider,
            model=self.current_model,
            session_id=self.current_session.id if self.current_session else None,
            message_provider=self.current_provider,
            message_model=self.current_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        ):
            # Extract session_id
            if 'session_id' in chunk and not session_id:
                session_id = chunk['session_id']
                if not self.current_session or self.current_session.id != session_id:
                    # Reload session to get updated info
                    self.current_session = await self.client.get_session(session_id)
            
            # Handle content
            if 'content' in chunk:
                content = chunk['content']
                full_content += content
                self.ui.print_chunk(content)
            
            # Handle reasoning/thinking
            if 'reasoning_content' in chunk:
                thinking_content += chunk['reasoning_content']
            
            # Handle errors
            if 'error' in chunk:
                has_error = True
                self.ui.print_streaming_end()
                self.ui.print_error(f"Error: {chunk['error']}")
                break
        
        if not has_error:
            self.ui.print_streaming_end()
            
            # Display thinking process if available
            if thinking_content:
                self.ui.print_thinking(thinking_content)
            
            # Update session message count
            if self.current_session and session_id:
                self.current_session.message_count += 2  # User + assistant
    
    async def _handle_non_streaming_response(self, messages: List[Message]):
        """Handle non-streaming chat response"""
        result = await self.client.chat(
            messages=messages,
            provider=self.current_provider,
            model=self.current_model,
            session_id=self.current_session.id if self.current_session else None,
            message_provider=self.current_provider,
            message_model=self.current_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        if result and 'message' in result:
            msg_data = result['message']
            assistant_message = Message(
                id=msg_data['id'],
                role=msg_data['role'],
                content=msg_data['content'],
                provider=msg_data.get('provider'),
                model=msg_data.get('model'),
                created_at=datetime.fromisoformat(msg_data['created_at'].replace('Z', '+00:00'))
            )
            
            self.ui.print_message(assistant_message, show_metadata=True)
            
            # Update session
            if 'session_id' in result:
                session_id = result['session_id']
                if not self.current_session or self.current_session.id != session_id:
                    self.current_session = await self.client.get_session(session_id)
                else:
                    self.current_session.message_count += 2
        else:
            self.ui.print_error("No response from server")
    
    async def switch_model(self, provider: str, model: str):
        """Switch to a different provider/model"""
        # Validate provider and model
        valid_model = None
        for m in self.models:
            if m.provider == provider and m.id == model:
                valid_model = m
                break
        
        if not valid_model:
            self.ui.print_error(f"Invalid provider/model combination: {provider}/{model}")
            return False
        
        self.current_provider = provider
        self.current_model = model
        self.ui.print_success(f"Switched to {provider}/{model}")
        return True
    
    async def handle_command(self, command: str) -> bool:
        """Handle slash commands. Returns False if should exit."""
        parts = command.split(maxsplit=2)
        cmd = parts[0].lower()
        
        # Exit commands
        if cmd in ['/stop', '/exit', '/quit']:
            return False
        
        # Help
        elif cmd == '/help':
            self.ui.show_help()
        
        # Clear screen
        elif cmd == '/clear':
            self.ui.clear()
            self.ui.show_welcome()
        
        # Session management
        elif cmd == '/new':
            title = parts[1] if len(parts) > 1 else None
            await self.create_session(title)
        
        elif cmd == '/sessions':
            sessions = await self.client.get_sessions()
            if sessions:
                self.ui.show_sessions(sessions)
            else:
                self.ui.print_info("No sessions found")
        
        elif cmd == '/load':
            if len(parts) < 2:
                self.ui.print_error("Usage: /load <session_id>")
            else:
                try:
                    session_id = int(parts[1])
                    await self.load_session(session_id)
                except ValueError:
                    self.ui.print_error("Session ID must be a number")
        
        elif cmd == '/delete':
            if len(parts) < 2:
                self.ui.print_error("Usage: /delete <session_id>")
            else:
                try:
                    session_id = int(parts[1])
                    if await self.client.delete_session(session_id):
                        self.ui.print_success(f"Deleted session {session_id}")
                        if self.current_session and self.current_session.id == session_id:
                            self.current_session = None
                    else:
                        self.ui.print_error(f"Failed to delete session {session_id}")
                except ValueError:
                    self.ui.print_error("Session ID must be a number")
        
        elif cmd == '/rename':
            if len(parts) < 2:
                self.ui.print_error("Usage: /rename <new_title>")
            elif not self.current_session:
                self.ui.print_error("No active session")
            else:
                new_title = ' '.join(parts[1:])
                if await self.client.update_session(self.current_session.id, new_title):
                    self.current_session.title = new_title
                    self.ui.print_success(f"Renamed session to: {new_title}")
                else:
                    self.ui.print_error("Failed to rename session")
        
        # Model management
        elif cmd == '/providers':
            if self.providers:
                self.ui.show_providers(self.providers)
            else:
                self.ui.print_info("No providers available")
        
        elif cmd == '/models':
            provider_filter = parts[1] if len(parts) > 1 else None
            models = await self.client.get_models(provider_filter)
            if models:
                self.ui.show_models(models, provider_filter)
            else:
                self.ui.print_info("No models found")
        
        elif cmd == '/switch':
            if len(parts) < 3:
                self.ui.print_error("Usage: /switch <provider> <model>")
            else:
                await self.switch_model(parts[1], parts[2])
        
        # Settings
        elif cmd == '/stream':
            if len(parts) < 2:
                self.ui.print_info(f"Streaming is currently {'enabled' if self.streaming_enabled else 'disabled'}")
            else:
                mode = parts[1].lower()
                if mode in ['on', 'true', 'yes', '1']:
                    self.streaming_enabled = True
                    self.ui.print_success("Streaming enabled")
                elif mode in ['off', 'false', 'no', '0']:
                    self.streaming_enabled = False
                    self.ui.print_success("Streaming disabled")
                else:
                    self.ui.print_error("Usage: /stream on|off")
        
        elif cmd == '/temp':
            if len(parts) < 2:
                self.ui.print_info(f"Current temperature: {self.temperature}")
            else:
                try:
                    temp = float(parts[1])
                    if 0.0 <= temp <= 2.0:
                        self.temperature = temp
                        self.ui.print_success(f"Temperature set to {temp}")
                    else:
                        self.ui.print_error("Temperature must be between 0.0 and 2.0")
                except ValueError:
                    self.ui.print_error("Invalid temperature value")
        
        elif cmd == '/info':
            if self.current_session:
                self.ui.show_session_info(self.current_session)
            else:
                self.ui.print_info(f"Provider: {self.current_provider}")
                self.ui.print_info(f"Model: {self.current_model}")
                self.ui.print_info(f"Streaming: {'enabled' if self.streaming_enabled else 'disabled'}")
                self.ui.print_info(f"Temperature: {self.temperature}")
        
        else:
            self.ui.print_error(f"Unknown command: {cmd}")
            self.ui.print_info("Type /help for available commands")
        
        return True
    
    async def run(self):
        """Main application loop"""
        try:
            # Initialize
            self.ui.clear()
            self.ui.print_header("Lite-LLM-Chat Terminal")
            
            if not await self.initialize():
                return
            
            self.ui.show_welcome()
            self.ui.print_info(f"Connected to backend at {self.backend_url}")
            self.ui.print_info(f"Default model: {self.current_provider}/{self.current_model}")
            self.ui.print_divider()
            
            # Main loop
            while True:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.prompt_session.prompt("\n> ")
                    )
                    
                    # Skip empty input
                    if not user_input.strip():
                        continue
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        should_continue = await self.handle_command(user_input)
                        if not should_continue:
                            self.ui.print_info("Goodbye!")
                            break
                    else:
                        # Send chat message
                        await self.send_message(user_input)
                
                except KeyboardInterrupt:
                    self.ui.print_warning("\nUse /exit to quit")
                    continue
                except EOFError:
                    self.ui.print_info("\nGoodbye!")
                    break
        
        finally:
            await self.cleanup()


async def main():
    """Entry point"""
    # Parse command line arguments
    backend_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
    
    app = ChatConsole(backend_url)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
