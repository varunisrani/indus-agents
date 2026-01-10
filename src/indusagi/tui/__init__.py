"""
Indus CLI - Terminal User Interface for IndusAGI

A modern, feature-rich TUI built with Textual, providing:
- Interactive chat sessions with AI agents
- Real-time streaming response display
- Tool execution visualization
- Multi-session management
- Customizable themes and keybindings
- Command palette for quick actions

Usage:
    from indusagi.tui import IndusApp
    app = IndusApp()
    app.run()

Or via CLI:
    indus tui
    indus tui --model gpt-4o --theme dark
"""

from indusagi.tui.app import IndusApp

__all__ = [
    "IndusApp",
]
