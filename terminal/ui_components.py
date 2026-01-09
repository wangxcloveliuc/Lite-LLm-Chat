"""
UI Components for Terminal Chat Application
Uses rich library for beautiful terminal output
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.style import Style
from typing import List, Optional
from datetime import datetime
from api_client import Provider, Model, Session, Message


console = Console()


class ChatUI:
    """User Interface components for chat application"""
    
    # Color scheme
    COLOR_USER = "cyan"
    COLOR_ASSISTANT = "green"
    COLOR_SYSTEM = "yellow"
    COLOR_THINKING = "magenta"
    COLOR_ERROR = "red"
    COLOR_INFO = "blue"
    COLOR_SUCCESS = "green"
    COLOR_WARNING = "yellow"
    
    @staticmethod
    def clear():
        """Clear the console"""
        console.clear()
    
    @staticmethod
    def print_header(text: str):
        """Print application header"""
        console.print(Panel(
            Text(text, style="bold white", justify="center"),
            border_style="bright_blue",
            padding=(1, 2)
        ))
    
    @staticmethod
    def print_info(message: str):
        """Print info message"""
        console.print(f"[{ChatUI.COLOR_INFO}]ℹ {message}[/]")
    
    @staticmethod
    def print_success(message: str):
        """Print success message"""
        console.print(f"[{ChatUI.COLOR_SUCCESS}]✓ {message}[/]")
    
    @staticmethod
    def print_warning(message: str):
        """Print warning message"""
        console.print(f"[{ChatUI.COLOR_WARNING}]⚠ {message}[/]")
    
    @staticmethod
    def print_error(message: str):
        """Print error message"""
        console.print(f"[{ChatUI.COLOR_ERROR}]✗ {message}[/]")
    
    @staticmethod
    def print_divider():
        """Print a divider line"""
        console.print("─" * console.width, style="dim")
    
    @staticmethod
    def show_providers(providers: List[Provider]):
        """Display available providers in a table"""
        table = Table(title="Available Providers", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")
        table.add_column("Status", justify="center")
        
        for provider in providers:
            status = "[green]✓[/]" if provider.supported else "[red]✗[/]"
            table.add_row(
                provider.id,
                provider.name,
                provider.description,
                status
            )
        
        console.print(table)
    
    @staticmethod
    def show_models(models: List[Model], provider_filter: Optional[str] = None):
        """Display available models in a table"""
        title = f"Models for {provider_filter}" if provider_filter else "All Available Models"
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Provider", style="yellow")
        table.add_column("Description", style="white")
        
        for model in models:
            table.add_row(
                model.id,
                model.name,
                model.provider,
                model.description
            )
        
        console.print(table)
    
    @staticmethod
    def show_sessions(sessions: List[Session]):
        """Display chat sessions in a table"""
        table = Table(title="Chat Sessions", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True, width=6)
        table.add_column("Title", style="green", max_width=40)
        table.add_column("Provider", style="yellow", width=12)
        table.add_column("Model", style="yellow", width=20)
        table.add_column("Messages", justify="right", width=10)
        table.add_column("Updated", style="dim", width=20)
        
        for session in sessions:
            updated = session.updated_at.strftime("%Y-%m-%d %H:%M")
            table.add_row(
                str(session.id),
                session.title,
                session.provider,
                session.model,
                str(session.message_count),
                updated
            )
        
        console.print(table)
    
    @staticmethod
    def show_session_info(session: Session):
        """Display current session information"""
        info_text = (
            f"[cyan]Session:[/] {session.id} | "
            f"[green]{session.title}[/] | "
            f"[yellow]{session.provider}/{session.model}[/] | "
            f"[dim]{session.message_count} messages[/]"
        )
        console.print(Panel(info_text, border_style="blue"))
    
    @staticmethod
    def print_message(message: Message, show_metadata: bool = False):
        """Print a chat message with formatting"""
        role = message.role
        content = message.content
        
        # Determine style based on role
        if role == "user":
            color = ChatUI.COLOR_USER
            icon = "👤"
            title = "You"
        elif role == "assistant":
            color = ChatUI.COLOR_ASSISTANT
            icon = "🤖"
            title = "Assistant"
        else:  # system
            color = ChatUI.COLOR_SYSTEM
            icon = "⚙️"
            title = "System"
        
        # Add metadata if requested
        metadata = ""
        if show_metadata and message.provider and message.model:
            metadata = f" [{message.provider}/{message.model}]"
        
        # Create title
        header = f"{icon} {title}{metadata}"

        # For assistant messages, show thinking before the final answer to match the streaming flow.
        if role == "assistant" and message.thought_process:
            ChatUI.print_thinking(message.thought_process)
        
        # Print message in a panel
        console.print(Panel(
            content,
            title=header,
            title_align="left",
            border_style=color,
            padding=(0, 2)
        ))

        # For non-assistant roles, keep any thought_process (if ever present) after the message.
        if role != "assistant" and message.thought_process:
            ChatUI.print_thinking(message.thought_process)
    
    @staticmethod
    def print_thinking_start():
        """Print start of thinking/reasoning process"""
        console.print(f"\n[{ChatUI.COLOR_THINKING}]🧠 Thinking:[/]", end=" ")
    
    @staticmethod
    def print_thinking_chunk(chunk: str):
        """Print a thinking chunk"""
        console.print(chunk, end="")
    
    @staticmethod
    def print_thinking_end():
        """Print end of thinking/reasoning process"""
        console.print("\n")
    
    @staticmethod
    def print_thinking(content: str):
        """Print model thinking/reasoning process (non-streaming)"""
        console.print(Panel(
            Markdown(content),
            title="🧠 Thinking",
            title_align="left",
            border_style=ChatUI.COLOR_THINKING,
            padding=(0, 2)
        ))
    
    @staticmethod
    def print_streaming_start(role: str = "assistant"):
        """Print start of streaming response"""
        if role == "assistant":
            console.print(f"\n[{ChatUI.COLOR_ASSISTANT}]🤖 Assistant:[/]", end=" ")
        else:
            console.print(f"\n[{ChatUI.COLOR_SYSTEM}]⚙️ System:[/]", end=" ")
    
    @staticmethod
    def print_chunk(chunk: str):
        """Print a streaming chunk"""
        console.print(chunk, end="")
    
    @staticmethod
    def print_streaming_end():
        """Print end of streaming response"""
        console.print("\n")
    
    @staticmethod
    def show_help():
        """Display help information"""
        help_text = """
**Available Commands:**

• **Chat Commands**
  - Type your message and press Enter to chat
  - `/stop` or `/exit` - Exit the application
  - `/clear` - Clear the conversation history display
  - `/help` - Show this help message

• **Session Management**
  - `/new <title>` - Create a new chat session
  - `/sessions` - List all sessions
  - `/load <session_id>` - Load an existing session
  - `/delete <session_id>` - Delete a session
  - `/rename <new_title>` - Rename current session

• **Model Management**
  - `/providers` - List available providers
  - `/models [provider]` - List available models (optionally filtered)
  - `/switch <provider> <model>` - Switch to a different model

• **Settings**
  - `/stream on|off` - Toggle streaming mode
  - `/temp <0.0-2.0>` - Set temperature (default: 1.0)
  - `/info` - Show current session info

**Tips:**
- Use streaming mode for real-time responses
- Switch models anytime during a conversation
- Model thinking process is displayed when available
- All messages are automatically saved to the session
"""
        console.print(Panel(
            Markdown(help_text),
            title="Help",
            border_style="blue",
            padding=(1, 2)
        ))
    
    @staticmethod
    def show_welcome():
        """Show welcome screen"""
        welcome = """
# Lite-LLM-Chat Terminal

Welcome to the interactive chat terminal! 

Type `/help` to see available commands.
Type `/exit` to quit.
"""
        console.print(Panel(
            Markdown(welcome),
            border_style="bright_blue",
            padding=(1, 2)
        ))
