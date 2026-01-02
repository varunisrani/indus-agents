# Phase 1: Foundation - Async Support & Core File Operations

## Overview

This phase establishes the core infrastructure needed for all subsequent features. Focus is on async capabilities and essential file manipulation tools.

---

## Objectives

1. Add async/await support to Agent and Orchestrator
2. Implement core file operation tools (Bash, Read, Write, Edit)
3. Create tool base class pattern
4. Ensure backward compatibility

---

## Task Breakdown

### 1.1 Async Agent Support

**File**: `src/my_agent_framework/agent.py`

**Changes**:
```python
import asyncio
from openai import AsyncOpenAI

class Agent:
    def __init__(self, ...):
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.sync_client = OpenAI(api_key=api_key)

    async def process(self, user_input: str) -> str:
        """Async processing with OpenAI"""
        self.messages.append({"role": "user", "content": user_input})
        response = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=self.messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )
        return response.choices[0].message.content

    def process_sync(self, user_input: str) -> str:
        """Sync wrapper for backward compatibility"""
        return asyncio.run(self.process(user_input))

    async def process_with_tools(
        self,
        user_input: str,
        tools: list = None,
        tool_executor = None,
        max_turns: int = 10
    ) -> str:
        """Async tool-enabled processing"""
        # Implementation with async tool execution
        pass
```

**Tests**:
- Test async processing
- Test sync wrapper
- Test with tools
- Test error handling

---

### 1.2 Tool Base Class

**File**: `src/my_agent_framework/tools/base.py`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Optional, Any
import asyncio

class BaseTool(BaseModel, ABC):
    """Base class for all indus-agents tools"""

    class Config:
        arbitrary_types_allowed = True

    # Optional context for cross-tool state
    context: Optional[Any] = Field(default=None, exclude=True)

    @abstractmethod
    async def run(self) -> str:
        """Execute the tool - must be implemented by subclasses"""
        pass

    def run_sync(self) -> str:
        """Synchronous execution wrapper"""
        return asyncio.run(self.run())

    def get_schema(self) -> dict:
        """Generate OpenAI-compatible tool schema"""
        schema = self.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.__class__.__name__.lower(),
                "description": self.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": {
                        k: v for k, v in schema.get("properties", {}).items()
                        if k != "context"
                    },
                    "required": [
                        k for k in schema.get("required", [])
                        if k != "context"
                    ]
                }
            }
        }
```

---

### 1.3 Bash Tool

**File**: `src/my_agent_framework/tools/bash.py`

```python
import asyncio
import subprocess
import threading
import platform
from pydantic import Field
from typing import Optional
from .base import BaseTool

_bash_lock = threading.Lock()

class Bash(BaseTool):
    """Execute bash commands with timeout and sandboxing.

    Use for system operations like running tests, installing packages,
    or executing scripts. Commands run in the current working directory.
    """

    command: str = Field(..., description="The bash command to execute")
    timeout: int = Field(
        default=120000,
        description="Timeout in milliseconds (max 600000)",
        ge=5000,
        le=600000
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the command"
    )

    async def run(self) -> str:
        """Execute the bash command"""
        timeout_seconds = self.timeout / 1000

        with _bash_lock:
            try:
                # Use asyncio subprocess for async execution
                process = await asyncio.create_subprocess_shell(
                    self.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=None  # Use current directory
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    return f"Exit code: 124\nCommand timed out after {timeout_seconds}s"

                output = stdout.decode() + stderr.decode()

                # Truncate if too long
                if len(output) > 30000:
                    output = output[-30000:]
                    output = f"[Output truncated, showing last 30000 chars]\n{output}"

                return f"Exit code: {process.returncode}\n{output}"

            except Exception as e:
                return f"Exit code: 1\nError: {str(e)}"

# Alias for tool loading
bash = Bash
```

---

### 1.4 Read Tool

**File**: `src/my_agent_framework/tools/read.py`

```python
import os
from pydantic import Field
from typing import Optional, Set
from .base import BaseTool

# Global tracking of read files (for write/edit preconditions)
_global_read_files: Set[str] = set()

class Read(BaseTool):
    """Read a file from the local filesystem.

    Use this to read file contents before editing. Supports text files,
    with line number display. Returns content with line numbers.
    """

    file_path: str = Field(
        ...,
        description="The absolute path to the file to read"
    )
    offset: Optional[int] = Field(
        default=None,
        description="Line number to start reading from (1-indexed)"
    )
    limit: Optional[int] = Field(
        default=2000,
        description="Number of lines to read"
    )

    async def run(self) -> str:
        """Read the file and return contents with line numbers"""
        global _global_read_files

        # Validate absolute path
        if not os.path.isabs(self.file_path):
            return f"Error: Path must be absolute: {self.file_path}"

        # Check file exists
        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        if os.path.isdir(self.file_path):
            return f"Error: Path is a directory, not a file: {self.file_path}"

        try:
            # Try UTF-8 first, fallback to latin-1
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()

            # Track that this file was read
            abs_path = os.path.abspath(self.file_path)
            _global_read_files.add(abs_path)

            # Also add to context if available
            if self.context is not None:
                read_files = self.context.get("read_files", set())
                read_files.add(abs_path)
                self.context.set("read_files", read_files)

            # Apply offset and limit
            start = (self.offset - 1) if self.offset else 0
            end = start + (self.limit or 2000)
            selected_lines = lines[start:end]

            if not selected_lines:
                return f"File is empty or offset is beyond file length: {self.file_path}"

            # Format with line numbers (cat -n style)
            result = []
            for i, line in enumerate(selected_lines, start=start + 1):
                # Truncate long lines
                if len(line) > 2000:
                    line = line[:2000] + "... [truncated]"
                result.append(f"{i:6d}\t{line.rstrip()}")

            return "\n".join(result)

        except PermissionError:
            return f"Error: Permission denied: {self.file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

# Alias for tool loading
read = Read
```

---

### 1.5 Write Tool

**File**: `src/my_agent_framework/tools/write.py`

```python
import os
from pydantic import Field
from .base import BaseTool
from .read import _global_read_files

class Write(BaseTool):
    """Write content to a file.

    Creates a new file or overwrites an existing one.
    IMPORTANT: You must use the Read tool first on existing files.
    """

    file_path: str = Field(
        ...,
        description="The absolute path to the file to write"
    )
    content: str = Field(
        ...,
        description="The content to write to the file"
    )

    async def run(self) -> str:
        """Write content to the file"""
        # Validate absolute path
        if not os.path.isabs(self.file_path):
            return f"Error: Path must be absolute: {self.file_path}"

        abs_path = os.path.abspath(self.file_path)
        file_exists = os.path.exists(self.file_path)

        # Check precondition: must read existing files first
        if file_exists:
            file_has_been_read = abs_path in _global_read_files

            if self.context is not None:
                read_files = self.context.get("read_files", set())
                file_has_been_read = file_has_been_read or abs_path in read_files

            if not file_has_been_read:
                return (
                    f"Error: You must use the Read tool before overwriting "
                    f"an existing file: {self.file_path}"
                )

        try:
            # Create directories if needed
            dir_path = os.path.dirname(self.file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # Write the content
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)

            # Track the write
            if self.context is not None:
                written_files = self.context.get("written_files", set())
                written_files.add(abs_path)
                self.context.set("written_files", written_files)

            # Get file stats
            size = os.path.getsize(self.file_path)
            line_count = self.content.count('\n') + (1 if self.content else 0)

            action = "overwritten" if file_exists else "created"
            return f"Successfully {action} file: {self.file_path}\nSize: {size} bytes, Lines: {line_count}"

        except PermissionError:
            return f"Error: Permission denied: {self.file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

# Alias for tool loading
write = Write
```

---

### 1.6 Edit Tool

**File**: `src/my_agent_framework/tools/edit.py`

```python
import os
from pydantic import Field
from typing import Optional
from .base import BaseTool
from .read import _global_read_files

class Edit(BaseTool):
    """Perform exact string replacements in a file.

    Replaces old_string with new_string. The old_string must be unique
    in the file unless replace_all is True.

    IMPORTANT: You must use the Read tool first before editing.
    """

    file_path: str = Field(
        ...,
        description="The absolute path to the file to edit"
    )
    old_string: str = Field(
        ...,
        description="The exact text to find and replace"
    )
    new_string: str = Field(
        ...,
        description="The text to replace old_string with"
    )
    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences (default: False, first match only)"
    )

    async def run(self) -> str:
        """Perform the string replacement"""
        # Validate absolute path
        if not os.path.isabs(self.file_path):
            return f"Error: Path must be absolute: {self.file_path}"

        # Check file exists
        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        # Validate strings are different
        if self.old_string == self.new_string:
            return "Error: old_string and new_string must be different"

        abs_path = os.path.abspath(self.file_path)

        # Check precondition: must read first
        file_has_been_read = abs_path in _global_read_files

        if self.context is not None:
            read_files = self.context.get("read_files", set())
            file_has_been_read = file_has_been_read or abs_path in read_files

        if not file_has_been_read:
            return (
                f"Error: You must use the Read tool before editing: {self.file_path}"
            )

        try:
            # Read current content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count occurrences
            occurrences = content.count(self.old_string)

            if occurrences == 0:
                # Show context to help debug
                preview = content[:500] + "..." if len(content) > 500 else content
                return (
                    f"Error: old_string not found in file.\n"
                    f"Looking for: {repr(self.old_string[:100])}\n"
                    f"File preview:\n{preview}"
                )

            if occurrences > 1 and not self.replace_all:
                # Show where matches are
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines, 1):
                    if self.old_string in line:
                        matches.append(f"  Line {i}: {line[:80]}...")
                        if len(matches) >= 5:
                            matches.append(f"  ... and {occurrences - 5} more")
                            break

                return (
                    f"Error: old_string appears {occurrences} times. "
                    f"Use replace_all=True or provide more context.\n"
                    f"Matches:\n" + "\n".join(matches)
                )

            # Perform replacement
            if self.replace_all:
                new_content = content.replace(self.old_string, self.new_string)
            else:
                new_content = content.replace(self.old_string, self.new_string, 1)

            # Write back
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Generate preview of change
            idx = content.find(self.old_string)
            start = max(0, idx - 30)
            end = min(len(content), idx + len(self.old_string) + 30)
            preview = f"...{content[start:end]}..."

            replaced_count = occurrences if self.replace_all else 1
            return (
                f"Successfully replaced {replaced_count} occurrence(s) in {self.file_path}\n"
                f"Context: {preview}"
            )

        except Exception as e:
            return f"Error editing file: {str(e)}"

# Alias for tool loading
edit = Edit
```

---

### 1.7 Tools Package Init

**File**: `src/my_agent_framework/tools/__init__.py`

```python
"""
indus-agents Tools Package

Provides file operation and system tools for agent workflows.
"""

from .base import BaseTool
from .bash import Bash
from .read import Read
from .write import Write
from .edit import Edit

__all__ = [
    "BaseTool",
    "Bash",
    "Read",
    "Write",
    "Edit",
]
```

---

## Testing Plan

### Unit Tests

```python
# tests/tools/test_bash.py
import pytest
from my_agent_framework.tools import Bash

@pytest.mark.asyncio
async def test_bash_simple():
    tool = Bash(command="echo 'hello'")
    result = await tool.run()
    assert "hello" in result
    assert "Exit code: 0" in result

@pytest.mark.asyncio
async def test_bash_timeout():
    tool = Bash(command="sleep 10", timeout=1000)
    result = await tool.run()
    assert "timed out" in result.lower()
```

### Integration Tests

```python
# tests/tools/test_file_operations.py
import pytest
import tempfile
from my_agent_framework.tools import Read, Write, Edit

@pytest.mark.asyncio
async def test_read_write_edit_flow():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World")
        path = f.name

    # Read
    read_tool = Read(file_path=path)
    content = await read_tool.run()
    assert "Hello World" in content

    # Edit
    edit_tool = Edit(
        file_path=path,
        old_string="World",
        new_string="Universe"
    )
    result = await edit_tool.run()
    assert "Successfully replaced" in result

    # Verify
    read_tool2 = Read(file_path=path)
    content2 = await read_tool2.run()
    assert "Hello Universe" in content2
```

---

## Acceptance Criteria

- [ ] Agent.process() works asynchronously
- [ ] Bash tool executes commands with timeout
- [ ] Read tool reads files with line numbers
- [ ] Write tool creates/overwrites files with precondition check
- [ ] Edit tool performs string replacement with uniqueness validation
- [ ] All tools have working sync wrappers
- [ ] 90%+ test coverage for new code
- [ ] Backward compatibility maintained

---

## Dependencies

```
# requirements.txt additions
aiofiles>=23.0.0
pytest-asyncio>=0.23.0
```

---

## Next Phase

After completing Phase 1, proceed to [Phase 2: Enhanced Tools](PHASE2_TOOLS.md) for Glob, Grep, Git, and additional developer tools.
