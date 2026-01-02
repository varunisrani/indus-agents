"""Shared utilities for indus-agents framework."""
from .agent_utils import (
    detect_model_type,
    select_instructions_file,
    render_instructions,
    create_model_settings,
    get_model_instance,
    ModelSettings,
)
from .system_hooks import AgentHooks, SystemReminderHook, create_system_reminder_hook
from .utils import silence_warnings_and_logs

__all__ = [
    "detect_model_type",
    "select_instructions_file",
    "render_instructions",
    "create_model_settings",
    "get_model_instance",
    "ModelSettings",
    "AgentHooks",
    "SystemReminderHook",
    "create_system_reminder_hook",
    "silence_warnings_and_logs",
]
