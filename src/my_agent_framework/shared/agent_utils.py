"""Agent creation utilities - model detection, instruction rendering, settings."""

import os
import platform
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ModelSettings:
    """Extended model configuration for different providers."""
    reasoning_effort: Optional[str] = None
    reasoning_summary: Optional[str] = "auto"
    max_tokens: int = 32000
    truncation: str = "auto"
    extra_body: Optional[Dict[str, Any]] = field(default=None)

def detect_model_type(model: str) -> Tuple[bool, bool, bool]:
    """
    Detect model provider type.

    Args:
        model: Model identifier string

    Returns:
        Tuple of (is_openai, is_claude, is_grok)
    """
    model_lower = model.lower()
    is_openai = "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower
    is_claude = "claude" in model_lower
    is_grok = "grok" in model_lower
    return is_openai, is_claude, is_grok

def select_instructions_file(base_dir: str, model: str) -> str:
    """
    Select model-specific instructions file.

    Args:
        base_dir: Base directory containing instruction files
        model: Model identifier to select instructions for

    Returns:
        Path to the appropriate instructions file
    """
    model_lower = model.lower()

    if model_lower.startswith("gpt-5") or model_lower.startswith("o1") or model_lower.startswith("o3"):
        filename = "instructions-gpt-5.md"
    elif "claude" in model_lower:
        filename = "instructions-claude.md"
    else:
        filename = "instructions.md"

    path = os.path.join(base_dir, filename)
    if os.path.exists(path):
        return path
    return os.path.join(base_dir, "instructions.md")

def render_instructions(
    template_path: str,
    model: str = "gpt-4o",
    extra_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Render instructions with placeholders replaced.

    Args:
        template_path: Path to the instruction template
        model: Model identifier for model-specific placeholders
        extra_context: Additional context variables to substitute

    Returns:
        Rendered instructions string
    """
    if not os.path.exists(template_path):
        return f"No instructions found at {template_path}"

    with open(template_path, "r") as f:
        content = f.read()

    # Standard placeholders
    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": str(os.path.isdir(os.path.join(os.getcwd(), ".git"))),
        "{platform}": platform.system(),
        "{os_version}": platform.release(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
        # Legacy placeholders for backward compatibility
        "{{cwd}}": os.getcwd(),
        "{{today}}": datetime.now().strftime("%Y-%m-%d"),
    }

    if extra_context:
        for key, value in extra_context.items():
            placeholders[f"{{{key}}}"] = str(value)
            placeholders[f"{{{{{key}}}}}"] = str(value)  # Also support double brace

    for key, value in placeholders.items():
        content = content.replace(key, value)

    return content

def create_model_settings(
    model: str,
    reasoning_effort: str = "medium",
    reasoning_summary: str = "auto",
    max_tokens: int = 32000
) -> ModelSettings:
    """
    Create model-specific settings.

    Args:
        model: Model identifier
        reasoning_effort: Reasoning effort level (low, medium, high)
        reasoning_summary: Reasoning summary mode
        max_tokens: Maximum tokens for response

    Returns:
        ModelSettings instance with appropriate configuration
    """
    is_openai, is_claude, is_grok = detect_model_type(model)

    return ModelSettings(
        reasoning_effort=reasoning_effort if (is_openai or is_claude) else None,
        reasoning_summary=reasoning_summary,
        max_tokens=max_tokens,
        truncation="auto",
        extra_body=(
            {"search_parameters": {"mode": "on", "returnCitations": True}}
            if is_grok else None
        ),
    )

def get_model_instance(model: str) -> str:
    """
    Get appropriate model instance based on provider.

    For multi-provider support, this would return the appropriate
    LiteLLM-wrapped model string.

    Args:
        model: Model identifier

    Returns:
        Model string for the appropriate provider
    """
    is_openai, is_claude, is_grok = detect_model_type(model)

    if is_openai:
        return model
    elif is_claude:
        # For Anthropic models via LiteLLM
        return f"anthropic/{model}" if not model.startswith("anthropic/") else model
    elif is_grok:
        # For X.AI models via LiteLLM
        return f"xai/{model}" if not model.startswith("xai/") else model

    # Default: return as-is
    return model
