# Phase 4: Advanced Features - Hooks, Streaming & Code Generation

## Overview

This phase adds production-ready features including a hook system for behavior customization, streaming responses, and the Genesis-like code generation capability for creating new agents.

---

## Objectives

1. Implement AgentHooks system for extensibility
2. Add system reminder and message filter hooks
3. Support streaming responses
4. Create notebook tools for Jupyter support
5. Build web search capability
6. Implement agent code generation (Genesis-like)

---

## Task Breakdown

### 4.1 Hooks System

**File**: `src/my_agent_framework/hooks.py`

```python
"""
Agent Hooks System

Provides extensibility points for customizing agent behavior.
Based on Agency Swarm's hook patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass
import asyncio

if TYPE_CHECKING:
    from .agent import Agent


@dataclass
class HookContext:
    """Context passed to hooks"""
    agent: "Agent"
    message: str
    tool_name: Optional[str] = None
    tool_result: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def set(self, key: str, value: Any):
        self.metadata[key] = value


class AgentHooks(ABC):
    """Base class for agent hooks"""

    async def on_start(self, context: HookContext) -> Optional[str]:
        """
        Called before agent processes a message.

        Returns:
            Optional modified message, or None to use original
        """
        pass

    async def on_end(self, context: HookContext, response: str) -> str:
        """
        Called after agent produces a response.

        Returns:
            Modified response
        """
        return response

    async def on_tool_start(self, context: HookContext) -> Optional[Dict]:
        """
        Called before a tool is executed.

        Returns:
            Optional modified tool arguments, or None to use original
        """
        pass

    async def on_tool_end(self, context: HookContext) -> Optional[str]:
        """
        Called after a tool completes.

        Returns:
            Optional modified result, or None to use original
        """
        pass

    async def on_error(self, context: HookContext, error: Exception) -> Optional[str]:
        """
        Called when an error occurs.

        Returns:
            Optional error message override, or None to use default
        """
        pass


class SystemReminderHook(AgentHooks):
    """
    Injects periodic reminders about important instructions.

    Similar to Agency-Code's SystemReminderHook, this adds
    reminders after every N tool calls or user messages.
    """

    def __init__(
        self,
        reminder_interval: int = 15,
        reminder_text: Optional[str] = None
    ):
        self.reminder_interval = reminder_interval
        self.tool_call_count = 0
        self.reminder_text = reminder_text or self._default_reminder()

    def _default_reminder(self) -> str:
        return """
REMINDER:
- Always read files before editing
- Prefer editing existing files over creating new ones
- Mark todo items completed immediately after finishing
- Do not add comments unless explicitly requested
"""

    def _get_todo_status(self, context: HookContext) -> str:
        """Get current todo status from context"""
        todos = context.get("todos", {})
        if not todos:
            return ""

        items = todos.get("items", [])
        pending = sum(1 for t in items if t.get("status") == "pending")
        in_progress = sum(1 for t in items if t.get("status") == "in_progress")
        completed = sum(1 for t in items if t.get("status") == "completed")

        status = f"\nTodo Status: {pending} pending, {in_progress} in progress, {completed} completed"

        in_progress_items = [t for t in items if t.get("status") == "in_progress"]
        if in_progress_items:
            status += f"\nCurrent task: {in_progress_items[0].get('content', 'Unknown')}"

        return status

    async def on_tool_end(self, context: HookContext) -> Optional[str]:
        """Increment counter and add reminder if needed"""
        self.tool_call_count += 1

        if self.tool_call_count >= self.reminder_interval:
            self.tool_call_count = 0
            todo_status = self._get_todo_status(context)
            context.set("pending_reminder", self.reminder_text + todo_status)

        return None

    async def on_start(self, context: HookContext) -> Optional[str]:
        """Add pending reminder to message if present"""
        pending = context.get("pending_reminder")
        if pending:
            context.set("pending_reminder", None)
            return f"{context.message}\n\n[System Reminder]\n{pending}"
        return None


class MessageFilterHook(AgentHooks):
    """
    Filters and preprocesses messages.

    Useful for:
    - Deduplicating messages
    - Reordering for API compatibility
    - Sanitizing inputs
    """

    def __init__(self, deduplicate: bool = True, sanitize: bool = True):
        self.deduplicate = deduplicate
        self.sanitize = sanitize
        self.seen_messages: set = set()

    async def on_start(self, context: HookContext) -> Optional[str]:
        """Filter incoming message"""
        message = context.message

        if self.sanitize:
            # Remove potentially harmful content
            message = self._sanitize(message)

        if self.deduplicate:
            # Check for duplicate
            msg_hash = hash(message[:200])  # Hash first 200 chars
            if msg_hash in self.seen_messages:
                context.set("is_duplicate", True)
            self.seen_messages.add(msg_hash)

        return message

    def _sanitize(self, message: str) -> str:
        """Basic input sanitization"""
        # Remove null bytes
        message = message.replace('\x00', '')

        # Limit message length
        if len(message) > 100000:
            message = message[:100000] + "\n[Message truncated]"

        return message


class LoggingHook(AgentHooks):
    """
    Logs all agent activity for debugging and monitoring.
    """

    def __init__(self, log_file: Optional[str] = None, verbose: bool = True):
        self.log_file = log_file
        self.verbose = verbose
        self.logs: List[Dict] = []

    def _log(self, event: str, data: Dict):
        """Log an event"""
        from datetime import datetime

        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data
        }

        self.logs.append(entry)

        if self.verbose:
            print(f"[{entry['timestamp']}] {event}: {data}")

        if self.log_file:
            import json
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')

    async def on_start(self, context: HookContext):
        self._log("agent_start", {
            "agent": context.agent.name,
            "message_length": len(context.message)
        })

    async def on_end(self, context: HookContext, response: str) -> str:
        self._log("agent_end", {
            "agent": context.agent.name,
            "response_length": len(response)
        })
        return response

    async def on_tool_start(self, context: HookContext):
        self._log("tool_start", {
            "tool": context.tool_name,
            "agent": context.agent.name
        })

    async def on_tool_end(self, context: HookContext):
        self._log("tool_end", {
            "tool": context.tool_name,
            "result_length": len(context.tool_result or "")
        })

    async def on_error(self, context: HookContext, error: Exception):
        self._log("error", {
            "agent": context.agent.name,
            "error": str(error)
        })


class CompositeHooks(AgentHooks):
    """
    Combines multiple hooks into one.

    Hooks are executed in order, with results chained.
    """

    def __init__(self, *hooks: AgentHooks):
        self.hooks = list(hooks)

    def add(self, hook: AgentHooks):
        self.hooks.append(hook)

    async def on_start(self, context: HookContext) -> Optional[str]:
        result = None
        for hook in self.hooks:
            hook_result = await hook.on_start(context)
            if hook_result is not None:
                context.message = hook_result
                result = hook_result
        return result

    async def on_end(self, context: HookContext, response: str) -> str:
        for hook in self.hooks:
            response = await hook.on_end(context, response)
        return response

    async def on_tool_start(self, context: HookContext) -> Optional[Dict]:
        result = None
        for hook in self.hooks:
            hook_result = await hook.on_tool_start(context)
            if hook_result is not None:
                result = hook_result
        return result

    async def on_tool_end(self, context: HookContext) -> Optional[str]:
        result = None
        for hook in self.hooks:
            hook_result = await hook.on_tool_end(context)
            if hook_result is not None:
                result = hook_result
        return result

    async def on_error(self, context: HookContext, error: Exception) -> Optional[str]:
        result = None
        for hook in self.hooks:
            hook_result = await hook.on_error(context, error)
            if hook_result is not None:
                result = hook_result
        return result
```

---

### 4.2 Notebook Tools

**File**: `src/my_agent_framework/tools/notebook_read.py`

```python
import os
import json
from pydantic import Field
from typing import Optional
from .base import BaseTool

class NotebookRead(BaseTool):
    """Read Jupyter notebook cells.

    Returns cell contents with outputs, execution counts, and metadata.
    """

    notebook_path: str = Field(
        ...,
        description="Absolute path to the .ipynb file"
    )
    cell_id: Optional[str] = Field(
        default=None,
        description="Specific cell ID or index to read (reads all if not specified)"
    )

    async def run(self) -> str:
        if not os.path.isabs(self.notebook_path):
            return f"Error: Path must be absolute: {self.notebook_path}"

        if not os.path.exists(self.notebook_path):
            return f"Error: File does not exist: {self.notebook_path}"

        if not self.notebook_path.endswith('.ipynb'):
            return f"Error: Not a notebook file: {self.notebook_path}"

        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            cells = notebook.get('cells', [])

            if not cells:
                return "Notebook has no cells"

            # If specific cell requested
            if self.cell_id is not None:
                cell = self._find_cell(cells, self.cell_id)
                if cell is None:
                    return f"Error: Cell not found: {self.cell_id}"
                return self._format_cell(cell, 0)

            # Format all cells
            result = f"Notebook: {self.notebook_path}\n"
            result += f"Total cells: {len(cells)}\n\n"

            for i, cell in enumerate(cells):
                result += self._format_cell(cell, i)
                result += "\n"

            return result

        except json.JSONDecodeError:
            return f"Error: Invalid notebook format: {self.notebook_path}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _find_cell(self, cells: list, cell_id: str) -> Optional[dict]:
        """Find cell by ID or index"""
        # Try as index first
        try:
            idx = int(cell_id)
            if 0 <= idx < len(cells):
                return cells[idx]
        except ValueError:
            pass

        # Try as cell ID
        for cell in cells:
            if cell.get('id') == cell_id:
                return cell

        return None

    def _format_cell(self, cell: dict, index: int) -> str:
        """Format a single cell for display"""
        cell_type = cell.get('cell_type', 'unknown')
        cell_id = cell.get('id', f'cell_{index}')
        source = ''.join(cell.get('source', []))

        result = f"=== Cell {index} (ID: {cell_id}, Type: {cell_type}) ===\n"
        result += f"Source:\n{source}\n"

        # Show outputs for code cells
        if cell_type == 'code':
            exec_count = cell.get('execution_count', '-')
            result += f"Execution count: {exec_count}\n"

            outputs = cell.get('outputs', [])
            if outputs:
                result += "Outputs:\n"
                for i, output in enumerate(outputs):
                    output_type = output.get('output_type', 'unknown')
                    result += f"  Output {i+1}: (Type: {output_type})\n"

                    if output_type == 'stream':
                        text = ''.join(output.get('text', []))
                        result += f"    {text[:500]}\n"
                    elif output_type in ['execute_result', 'display_data']:
                        data = output.get('data', {})
                        if 'text/plain' in data:
                            text = ''.join(data['text/plain'])
                            result += f"    {text[:500]}\n"
                    elif output_type == 'error':
                        ename = output.get('ename', 'Error')
                        evalue = output.get('evalue', '')
                        result += f"    {ename}: {evalue}\n"

        return result

notebook_read = NotebookRead
```

**File**: `src/my_agent_framework/tools/notebook_edit.py`

```python
import os
import json
import uuid
from pydantic import Field
from typing import Optional, Literal
from .base import BaseTool

class NotebookEdit(BaseTool):
    """Edit Jupyter notebook cells.

    Supports replace, insert, and delete operations.
    """

    notebook_path: str = Field(
        ...,
        description="Absolute path to the .ipynb file"
    )
    cell_id: Optional[str] = Field(
        default=None,
        description="Cell ID or index to edit (required for replace/delete)"
    )
    new_source: str = Field(
        ...,
        description="New cell content"
    )
    cell_type: Optional[Literal["code", "markdown"]] = Field(
        default=None,
        description="Cell type (required for insert)"
    )
    edit_mode: Literal["replace", "insert", "delete"] = Field(
        default="replace",
        description="Edit mode: replace, insert, or delete"
    )

    async def run(self) -> str:
        if not os.path.isabs(self.notebook_path):
            return f"Error: Path must be absolute: {self.notebook_path}"

        if not os.path.exists(self.notebook_path):
            return f"Error: File does not exist: {self.notebook_path}"

        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            cells = notebook.get('cells', [])

            if self.edit_mode == "replace":
                result = self._replace_cell(cells)
            elif self.edit_mode == "insert":
                result = self._insert_cell(cells)
            elif self.edit_mode == "delete":
                result = self._delete_cell(cells)
            else:
                return f"Error: Unknown edit mode: {self.edit_mode}"

            if result.startswith("Error"):
                return result

            # Save notebook
            notebook['cells'] = cells
            with open(self.notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1)

            return result

        except Exception as e:
            return f"Error: {str(e)}"

    def _find_cell_index(self, cells: list) -> Optional[int]:
        """Find cell index by ID or direct index"""
        if self.cell_id is None:
            return None

        try:
            idx = int(self.cell_id)
            if 0 <= idx < len(cells):
                return idx
        except ValueError:
            pass

        for i, cell in enumerate(cells):
            if cell.get('id') == self.cell_id:
                return i

        return None

    def _replace_cell(self, cells: list) -> str:
        """Replace cell content"""
        idx = self._find_cell_index(cells)
        if idx is None:
            return f"Error: Cell not found: {self.cell_id}"

        cell = cells[idx]
        cell['source'] = self.new_source.split('\n')

        if self.cell_type:
            cell['cell_type'] = self.cell_type

        if cell.get('cell_type') == 'code':
            cell['execution_count'] = None
            cell['outputs'] = []

        return f"Successfully replaced cell {idx}"

    def _insert_cell(self, cells: list) -> str:
        """Insert new cell"""
        if not self.cell_type:
            return "Error: cell_type is required for insert"

        new_cell = {
            'cell_type': self.cell_type,
            'id': str(uuid.uuid4())[:8],
            'source': self.new_source.split('\n'),
            'metadata': {}
        }

        if self.cell_type == 'code':
            new_cell['execution_count'] = None
            new_cell['outputs'] = []

        if self.cell_id:
            idx = self._find_cell_index(cells)
            if idx is not None:
                cells.insert(idx + 1, new_cell)
                return f"Successfully inserted cell after {idx}"

        cells.append(new_cell)
        return f"Successfully inserted cell at end"

    def _delete_cell(self, cells: list) -> str:
        """Delete a cell"""
        idx = self._find_cell_index(cells)
        if idx is None:
            return f"Error: Cell not found: {self.cell_id}"

        deleted = cells.pop(idx)
        return f"Successfully deleted cell {idx} (type: {deleted.get('cell_type')})"

notebook_edit = NotebookEdit
```

---

### 4.3 Web Search Tool

**File**: `src/my_agent_framework/tools/web_search.py`

```python
import os
from pydantic import Field
from typing import Optional, List
from .base import BaseTool

class WebSearch(BaseTool):
    """Search the web for information.

    Uses available search APIs (SerpAPI, Tavily, etc.)
    """

    query: str = Field(
        ...,
        description="Search query"
    )
    num_results: int = Field(
        default=5,
        description="Number of results to return",
        ge=1,
        le=20
    )

    async def run(self) -> str:
        # Try different search providers
        if os.getenv("SERPAPI_API_KEY"):
            return await self._search_serpapi()
        elif os.getenv("TAVILY_API_KEY"):
            return await self._search_tavily()
        else:
            return self._no_api_message()

    async def _search_serpapi(self) -> str:
        """Search using SerpAPI"""
        try:
            import httpx

            api_key = os.getenv("SERPAPI_API_KEY")
            url = "https://serpapi.com/search"
            params = {
                "q": self.query,
                "api_key": api_key,
                "num": self.num_results
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30)
                data = response.json()

            results = data.get("organic_results", [])
            return self._format_results(results)

        except Exception as e:
            return f"Search error: {str(e)}"

    async def _search_tavily(self) -> str:
        """Search using Tavily"""
        try:
            import httpx

            api_key = os.getenv("TAVILY_API_KEY")
            url = "https://api.tavily.com/search"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "api_key": api_key,
                        "query": self.query,
                        "max_results": self.num_results
                    },
                    timeout=30
                )
                data = response.json()

            results = data.get("results", [])
            return self._format_results(results)

        except Exception as e:
            return f"Search error: {str(e)}"

    def _format_results(self, results: List[dict]) -> str:
        """Format search results"""
        if not results:
            return f"No results found for: {self.query}"

        output = f"Search results for: {self.query}\n\n"

        for i, result in enumerate(results[:self.num_results], 1):
            title = result.get("title", "No title")
            url = result.get("link") or result.get("url", "No URL")
            snippet = result.get("snippet") or result.get("content", "No description")

            output += f"{i}. {title}\n"
            output += f"   URL: {url}\n"
            output += f"   {snippet[:200]}...\n\n"

        return output

    def _no_api_message(self) -> str:
        return """Web search requires an API key. Set one of:
- SERPAPI_API_KEY for SerpAPI
- TAVILY_API_KEY for Tavily

Get keys at:
- https://serpapi.com
- https://tavily.com
"""

web_search = WebSearch
```

---

### 4.4 Genesis - Agent Code Generator

**File**: `src/my_agent_framework/genesis/__init__.py`

```python
"""
Genesis - Agent Code Generator

Create new agents and tools using AI.
Similar to Agency Swarm's Genesis capability.
"""

from .agent_creator import AgentCreator, create_agent_from_spec
from .tool_creator import ToolCreator, create_tool_from_spec

__all__ = [
    "AgentCreator",
    "ToolCreator",
    "create_agent_from_spec",
    "create_tool_from_spec",
]
```

**File**: `src/my_agent_framework/genesis/agent_creator.py`

```python
"""
Agent Creator - Generate new agent code from specifications
"""

import os
from typing import Optional
from ..agent import Agent, AgentConfig
from ..tools import Read, Write, Glob

AGENT_TEMPLATE = '''"""
{name} Agent

{description}
"""

import os
from typing import Optional
from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.tools import {tools_import}


def load_instructions(base_dir: str) -> str:
    """Load agent instructions"""
    filepath = os.path.join(base_dir, "instructions", "{name_lower}.md")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return """{default_instructions}"""


def create_{name_lower}_agent(
    model: str = "{default_model}",
    name: str = "{name}",
    **kwargs
) -> Agent:
    """
    Create a {name} agent.

    Args:
        model: LLM model to use
        name: Agent name
        **kwargs: Additional configuration

    Returns:
        Configured Agent instance
    """
    base_dir = os.path.dirname(__file__)
    instructions = load_instructions(base_dir)

    config = AgentConfig(
        model=model,
        temperature={temperature},
        max_tokens=4096,
        **kwargs
    )

    agent = Agent(
        name=name,
        role="{role}",
        config=config,
        system_prompt=instructions
    )

    agent.tools = [{tools_list}]

    return agent
'''

INSTRUCTIONS_TEMPLATE = '''# {name} Agent Instructions

{description}

## Core Responsibilities
{responsibilities}

## Working Principles
{principles}

## Tool Usage
{tool_usage}
'''


class AgentCreator:
    """Creates new agent code from specifications"""

    def __init__(self, output_dir: str = "agents"):
        self.output_dir = output_dir

    async def create(
        self,
        name: str,
        description: str,
        role: str,
        tools: list = None,
        responsibilities: list = None,
        principles: list = None,
        model: str = "gpt-4o",
        temperature: float = 0.5
    ) -> dict:
        """
        Create a new agent with code and instructions.

        Args:
            name: Agent name (e.g., "DataAnalyst")
            description: Agent description
            role: Agent role
            tools: List of tool classes to include
            responsibilities: List of responsibilities
            principles: List of working principles
            model: Default model
            temperature: Default temperature

        Returns:
            Dict with file paths created
        """
        name_lower = name.lower().replace(" ", "_")
        agent_dir = os.path.join(self.output_dir, f"{name_lower}_agent")
        instructions_dir = os.path.join(agent_dir, "instructions")

        # Create directories
        os.makedirs(instructions_dir, exist_ok=True)

        # Generate tools import and list
        tools = tools or []
        tool_names = [t.__name__ for t in tools]
        tools_import = ", ".join(tool_names) if tool_names else "BaseTool"
        tools_list = ", ".join(tool_names) if tool_names else ""

        # Generate responsibilities text
        resp_text = "\n".join(f"- {r}" for r in (responsibilities or ["Assist with tasks"]))

        # Generate principles text
        princ_text = "\n".join(f"- {p}" for p in (principles or ["Be helpful and efficient"]))

        # Generate tool usage text
        tool_text = "\n".join(f"- Use `{t}` for {t.lower().replace('_', ' ')}" for t in tool_names) or "No special tools"

        # Generate agent code
        agent_code = AGENT_TEMPLATE.format(
            name=name,
            name_lower=name_lower,
            description=description,
            role=role,
            tools_import=tools_import,
            tools_list=tools_list,
            default_model=model,
            temperature=temperature,
            default_instructions=f"You are a {role}. {description}"
        )

        # Generate instructions
        instructions = INSTRUCTIONS_TEMPLATE.format(
            name=name,
            description=description,
            responsibilities=resp_text,
            principles=princ_text,
            tool_usage=tool_text
        )

        # Write files
        agent_file = os.path.join(agent_dir, f"{name_lower}_agent.py")
        init_file = os.path.join(agent_dir, "__init__.py")
        instructions_file = os.path.join(instructions_dir, f"{name_lower}.md")

        with open(agent_file, 'w') as f:
            f.write(agent_code)

        with open(init_file, 'w') as f:
            f.write(f'from .{name_lower}_agent import create_{name_lower}_agent\n')

        with open(instructions_file, 'w') as f:
            f.write(instructions)

        return {
            "agent_file": agent_file,
            "init_file": init_file,
            "instructions_file": instructions_file,
            "agent_dir": agent_dir
        }


async def create_agent_from_spec(spec: dict, output_dir: str = "agents") -> dict:
    """
    Create an agent from a specification dictionary.

    Args:
        spec: Dictionary with agent specification
        output_dir: Output directory

    Returns:
        Dict with created file paths
    """
    creator = AgentCreator(output_dir)
    return await creator.create(**spec)
```

**File**: `src/my_agent_framework/genesis/tool_creator.py`

```python
"""
Tool Creator - Generate new tool code from specifications
"""

import os
from typing import List, Dict, Any

TOOL_TEMPLATE = '''"""
{name} Tool

{description}
"""

from pydantic import Field
from typing import Optional{extra_imports}
from my_agent_framework.tools.base import BaseTool


class {class_name}(BaseTool):
    """{description}

    {usage_notes}
    """

{parameters}

    async def run(self) -> str:
        """Execute the tool"""
        try:
{implementation}
        except Exception as e:
            return f"Error: {{str(e)}}"


# Alias for tool loading
{alias} = {class_name}
'''


class ToolCreator:
    """Creates new tool code from specifications"""

    def __init__(self, output_dir: str = "tools"):
        self.output_dir = output_dir

    async def create(
        self,
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        implementation: str,
        usage_notes: str = "",
        extra_imports: List[str] = None
    ) -> dict:
        """
        Create a new tool with code.

        Args:
            name: Tool name (e.g., "DataFetcher")
            description: Tool description
            parameters: List of parameter definitions
            implementation: Python code for the run method body
            usage_notes: Additional usage documentation
            extra_imports: Extra import statements

        Returns:
            Dict with file path created
        """
        class_name = name
        alias = name.lower()
        filename = f"{alias}.py"

        # Generate parameters
        param_lines = []
        for param in parameters:
            param_name = param["name"]
            param_type = param.get("type", "str")
            param_desc = param.get("description", "")
            param_default = param.get("default")

            if param_default is not None:
                if isinstance(param_default, str):
                    default_str = f'default="{param_default}"'
                else:
                    default_str = f"default={param_default}"
                param_lines.append(
                    f'    {param_name}: {param_type} = Field({default_str}, description="{param_desc}")'
                )
            else:
                param_lines.append(
                    f'    {param_name}: {param_type} = Field(..., description="{param_desc}")'
                )

        params_str = "\n".join(param_lines) if param_lines else "    pass"

        # Format implementation with proper indentation
        impl_lines = implementation.strip().split('\n')
        impl_str = '\n'.join(f'            {line}' for line in impl_lines)

        # Format extra imports
        imports_str = ""
        if extra_imports:
            imports_str = "\n" + "\n".join(extra_imports)

        # Generate code
        code = TOOL_TEMPLATE.format(
            name=name,
            class_name=class_name,
            description=description,
            usage_notes=usage_notes,
            parameters=params_str,
            implementation=impl_str,
            alias=alias,
            extra_imports=imports_str
        )

        # Write file
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(code)

        return {
            "tool_file": filepath,
            "class_name": class_name,
            "alias": alias
        }


async def create_tool_from_spec(spec: dict, output_dir: str = "tools") -> dict:
    """
    Create a tool from a specification dictionary.

    Args:
        spec: Dictionary with tool specification
        output_dir: Output directory

    Returns:
        Dict with created file path
    """
    creator = ToolCreator(output_dir)
    return await creator.create(**spec)
```

---

## Updated Package Init

**File**: `src/my_agent_framework/__init__.py`

```python
"""
indus-agents - Multi-Agent Framework with Agency Swarm Features

A comprehensive framework for building intelligent AI agents with:
- Multi-LLM support (OpenAI, Anthropic, LiteLLM)
- Inter-agent communication (handoffs)
- Extensible tool system
- Hook-based customization
- Code generation capabilities
"""

__version__ = "0.2.0"
__author__ = "indus-agents Team"
__license__ = "MIT"

# Core
from .agent import Agent, AgentConfig
from .orchestrator import MultiAgentOrchestrator, OrchestratorResponse, create_orchestrator
from .memory import ConversationMemory, Message

# Tools
from .tools import (
    BaseTool, ToolRegistry, registry,
    Bash, Read, Write, Edit, MultiEdit,
    Glob, Grep, Git, LS, TodoWrite
)

# LLM Providers
from .llm import (
    LLMProvider, OpenAIProvider, AnthropicProvider, LiteLLMProvider,
    get_provider, detect_model_type
)

# Agency (Multi-agent with handoffs)
from .agency import Agency, AgencyResponse, create_agency
from .handoff import SendMessageHandoff, HandoffConfig

# Hooks
from .hooks import (
    AgentHooks, HookContext,
    SystemReminderHook, MessageFilterHook, LoggingHook, CompositeHooks
)

# Pre-built agents
from .agents import create_developer_agent, create_planner_agent

# Genesis (Code generation)
from .genesis import (
    AgentCreator, ToolCreator,
    create_agent_from_spec, create_tool_from_spec
)

__all__ = [
    # Version
    "__version__",

    # Core
    "Agent", "AgentConfig",
    "MultiAgentOrchestrator", "OrchestratorResponse", "create_orchestrator",
    "ConversationMemory", "Message",

    # Tools
    "BaseTool", "ToolRegistry", "registry",
    "Bash", "Read", "Write", "Edit", "MultiEdit",
    "Glob", "Grep", "Git", "LS", "TodoWrite",

    # LLM
    "LLMProvider", "OpenAIProvider", "AnthropicProvider", "LiteLLMProvider",
    "get_provider", "detect_model_type",

    # Agency
    "Agency", "AgencyResponse", "create_agency",
    "SendMessageHandoff", "HandoffConfig",

    # Hooks
    "AgentHooks", "HookContext",
    "SystemReminderHook", "MessageFilterHook", "LoggingHook", "CompositeHooks",

    # Agents
    "create_developer_agent", "create_planner_agent",

    # Genesis
    "AgentCreator", "ToolCreator",
    "create_agent_from_spec", "create_tool_from_spec",
]
```

---

## Acceptance Criteria

- [ ] Hook system works with all lifecycle events
- [ ] SystemReminderHook triggers correctly
- [ ] MessageFilterHook sanitizes input
- [ ] NotebookRead displays cells correctly
- [ ] NotebookEdit modifies notebooks atomically
- [ ] WebSearch works with available APIs
- [ ] AgentCreator generates valid agent code
- [ ] ToolCreator generates valid tool code
- [ ] All features have tests
- [ ] Documentation updated

---

## Conclusion

Phase 4 completes the transformation of indus-agents into a production-ready framework with Agency Swarm-like capabilities. The Genesis system enables the framework to create new agents and tools dynamically, similar to Agency-Code's code generation features.
