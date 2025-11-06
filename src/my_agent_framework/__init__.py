"""
My Agent Framework - AI Agent Framework with Multi-Agent Orchestration

A production-ready AI agent framework featuring:
- OpenAI GPT-4o integration with tool calling
- Multi-agent orchestration with intelligent routing
- Conversation memory management
- Beautiful CLI interface
- 9 built-in tools
- Comprehensive testing (92% coverage)

Quick Start:
    >>> from my_agent_framework import Agent, create_orchestrator
    >>>
    >>> # Single agent
    >>> agent = Agent("Helper", "Helpful assistant")
    >>> response = agent.process("What is 2+2?")
    >>>
    >>> # Multi-agent orchestrator (recommended)
    >>> orchestrator = create_orchestrator()
    >>> response = orchestrator.process("Calculate 25 * 4")
    >>> print(response.response)

Installation:
    pip install -e .

CLI Usage:
    my-agent run "What is 25 * 48?"
    my-agent interactive
    my-agent list-tools

For more information, see README.md
"""

__version__ = "0.1.0"
__author__ = "AI Agent Framework Team"
__email__ = "contact@example.com"
__license__ = "MIT"

# Core imports from working implementation files
from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.tools import registry, ToolRegistry
from my_agent_framework.orchestrator import MultiAgentOrchestrator, OrchestratorResponse, create_orchestrator
from my_agent_framework.memory import ConversationMemory, Message

# Expose public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",

    # Core classes
    "Agent",
    "AgentConfig",

    # Tool system
    "ToolRegistry",
    "registry",

    # Orchestrator
    "MultiAgentOrchestrator",
    "OrchestratorResponse",
    "create_orchestrator",

    # Memory
    "ConversationMemory",
    "Message",
]

# Convenience function
def get_version() -> str:
    """Get the current version of the framework."""
    return __version__
