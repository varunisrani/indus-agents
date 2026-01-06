"""
Utility functions for loading agent prompts from markdown files.

Supports:
- Loading prompts from .md files
- Model-specific prompt selection
- Fallback to default prompts
"""
import os
from pathlib import Path
from typing import Optional


def load_prompt_from_file(file_path: str) -> str:
    """
    Load prompt content from a markdown file.

    Args:
        file_path: Path to the .md file (absolute or relative)

    Returns:
        Content of the file as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If the file can't be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    if not path.is_file():
        raise IOError(f"Path is not a file: {file_path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            raise IOError(f"Prompt file is empty: {file_path}")

        return content
    except Exception as e:
        raise IOError(f"Failed to read prompt file {file_path}: {str(e)}")


def select_prompt_file(base_dir: str, base_name: str, model: str) -> str:
    """
    Select appropriate prompt file based on model type.

    Looks for model-specific files first (e.g., instructions-gpt-5.md),
    then falls back to base file (e.g., instructions.md).

    Args:
        base_dir: Directory containing prompt files
        base_name: Base name without extension (e.g., "instructions")
        model: Model name (e.g., "gpt-5", "claude-sonnet-4")

    Returns:
        Absolute path to the selected prompt file

    Raises:
        FileNotFoundError: If no suitable prompt file is found
    """
    base_path = Path(base_dir)

    # Try model-specific file first
    if model.lower().startswith("gpt-5"):
        model_specific = base_path / f"{base_name}-gpt-5.md"
        if model_specific.exists():
            return str(model_specific.absolute())

    if model.lower().startswith("claude"):
        model_specific = base_path / f"{base_name}-claude.md"
        if model_specific.exists():
            return str(model_specific.absolute())

    # Fall back to base file
    base_file = base_path / f"{base_name}.md"
    if base_file.exists():
        return str(base_file.absolute())

    raise FileNotFoundError(
        f"No prompt file found in {base_dir} for base name '{base_name}'"
    )


def is_file_path(text: str) -> bool:
    """
    Check if a string looks like a file path.

    Args:
        text: String to check

    Returns:
        True if the string appears to be a file path
    """
    # Check for common file path indicators
    if not text:
        return False

    # Check for file extensions
    if text.endswith('.md') or text.endswith('.txt'):
        return True

    # Check for path separators
    if '/' in text or '\\' in text:
        return True

    # Check if it's an existing file
    path = Path(text)
    if path.exists() and path.is_file():
        return True

    return False
