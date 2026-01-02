# Phase 2: Enhanced Tools - Complete Developer Toolkit

## Overview

This phase adds advanced search, file discovery, version control, and task management tools to complete the developer workflow capabilities.

---

## Objectives

1. Implement file discovery tools (Glob, LS)
2. Add content search capabilities (Grep)
3. Integrate Git operations
4. Implement MultiEdit for atomic changes
5. Add TodoWrite for task management

---

## Task Breakdown

### 2.1 Glob Tool

**File**: `src/my_agent_framework/tools/glob.py`

```python
import os
import fnmatch
from pathlib import Path
from pydantic import Field
from typing import Optional, List
from .base import BaseTool

class Glob(BaseTool):
    """Fast file pattern matching.

    Find files matching glob patterns like '**/*.py' or 'src/**/*.ts'.
    Respects .gitignore patterns. Returns files sorted by modification time.
    """

    pattern: str = Field(
        ...,
        description="Glob pattern (e.g., '**/*.py', 'src/**/*.ts')"
    )
    path: Optional[str] = Field(
        default=None,
        description="Directory to search in (default: current directory)"
    )

    async def run(self) -> str:
        """Find files matching the pattern"""
        search_dir = self.path or os.getcwd()

        if not os.path.isabs(search_dir):
            search_dir = os.path.abspath(search_dir)

        if not os.path.isdir(search_dir):
            return f"Error: Directory does not exist: {search_dir}"

        try:
            # Load gitignore patterns
            gitignore_patterns = self._load_gitignore(search_dir)

            # Find matching files
            matches = []
            for root, dirs, files in os.walk(search_dir):
                # Filter ignored directories
                dirs[:] = [d for d in dirs if not self._is_ignored(
                    os.path.join(root, d), search_dir, gitignore_patterns
                )]

                for filename in files:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, search_dir)

                    if self._matches_pattern(rel_path, self.pattern):
                        if not self._is_ignored(filepath, search_dir, gitignore_patterns):
                            matches.append(filepath)

            # Sort by modification time (newest first)
            matches.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            if not matches:
                return f"No files found matching '{self.pattern}' in {search_dir}"

            result = f"Found {len(matches)} files matching '{self.pattern}':\n\n"
            for match in matches[:100]:  # Limit to 100 results
                result += f"{match}\n"

            if len(matches) > 100:
                result += f"\n... and {len(matches) - 100} more files"

            return result

        except Exception as e:
            return f"Error: {str(e)}"

    def _load_gitignore(self, directory: str) -> List[str]:
        """Load patterns from .gitignore"""
        patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        gitignore_path = os.path.join(directory, '.gitignore')

        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except:
                pass

        return patterns

    def _is_ignored(self, path: str, base_dir: str, patterns: List[str]) -> bool:
        """Check if path matches any ignore pattern"""
        rel_path = os.path.relpath(path, base_dir)
        name = os.path.basename(path)

        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
            if fnmatch.fnmatch(rel_path, pattern):
                return True

        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches the glob pattern"""
        # Handle ** for recursive matching
        if '**' in pattern:
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                suffix = suffix.lstrip('/')
                if prefix:
                    if not path.startswith(prefix.rstrip('/')):
                        return False
                if suffix:
                    return fnmatch.fnmatch(path, f'*{suffix}') or \
                           fnmatch.fnmatch(os.path.basename(path), suffix)
                return True

        return fnmatch.fnmatch(path, pattern) or \
               fnmatch.fnmatch(os.path.basename(path), pattern)

# Alias for tool loading
glob = Glob
```

---

### 2.2 Grep Tool

**File**: `src/my_agent_framework/tools/grep.py`

```python
import os
import re
import subprocess
from pydantic import Field
from typing import Optional, Literal
from .base import BaseTool

class Grep(BaseTool):
    """Search file contents using regex patterns.

    Powered by ripgrep (rg) if available, falls back to Python regex.
    Supports multiple output modes: content, files_with_matches, count.
    """

    pattern: str = Field(
        ...,
        description="Regular expression pattern to search for"
    )
    path: Optional[str] = Field(
        default=".",
        description="Directory or file to search in"
    )
    glob: Optional[str] = Field(
        default=None,
        description="File pattern filter (e.g., '*.py', '*.{ts,tsx}')"
    )
    output_mode: Optional[Literal["content", "files_with_matches", "count"]] = Field(
        default="files_with_matches",
        description="Output mode: content (show lines), files_with_matches, or count"
    )
    case_insensitive: Optional[bool] = Field(
        default=False,
        alias="-i",
        description="Case insensitive search"
    )
    context_lines: Optional[int] = Field(
        default=None,
        alias="-C",
        description="Lines of context before and after match"
    )
    max_results: Optional[int] = Field(
        default=50,
        description="Maximum number of results to return"
    )

    async def run(self) -> str:
        """Execute the search"""
        search_path = self.path or "."
        if not os.path.isabs(search_path):
            search_path = os.path.abspath(search_path)

        if not os.path.exists(search_path):
            return f"Error: Path does not exist: {search_path}"

        # Try ripgrep first
        if self._has_ripgrep():
            return await self._search_ripgrep(search_path)
        else:
            return await self._search_python(search_path)

    def _has_ripgrep(self) -> bool:
        """Check if ripgrep is available"""
        try:
            subprocess.run(['rg', '--version'], capture_output=True)
            return True
        except:
            return False

    async def _search_ripgrep(self, search_path: str) -> str:
        """Search using ripgrep"""
        cmd = ['rg']

        # Output mode
        if self.output_mode == "files_with_matches":
            cmd.append('-l')
        elif self.output_mode == "count":
            cmd.append('-c')
        else:
            cmd.append('-n')  # Line numbers for content mode

        # Options
        if self.case_insensitive:
            cmd.append('-i')

        if self.context_lines:
            cmd.extend(['-C', str(self.context_lines)])

        if self.glob:
            cmd.extend(['--glob', self.glob])

        cmd.extend([self.pattern, search_path])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                lines = output.strip().split('\n')
                if len(lines) > self.max_results:
                    output = '\n'.join(lines[:self.max_results])
                    output += f"\n\n... and {len(lines) - self.max_results} more matches"
                return f"Exit code: 0\n{output}"
            elif result.returncode == 1:
                return "Exit code: 1\nNo matches found"
            else:
                return f"Exit code: {result.returncode}\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return "Exit code: 124\nSearch timed out"
        except Exception as e:
            return f"Exit code: 1\nError: {str(e)}"

    async def _search_python(self, search_path: str) -> str:
        """Fallback Python-based search"""
        try:
            regex = re.compile(
                self.pattern,
                re.IGNORECASE if self.case_insensitive else 0
            )
        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"

        matches = []
        file_matches = {}

        def search_file(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            if filepath not in file_matches:
                                file_matches[filepath] = []
                            file_matches[filepath].append((i, line.rstrip()))
            except:
                pass

        if os.path.isfile(search_path):
            search_file(search_path)
        else:
            for root, dirs, files in os.walk(search_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
                for filename in files:
                    if self.glob:
                        import fnmatch
                        if not fnmatch.fnmatch(filename, self.glob):
                            continue
                    filepath = os.path.join(root, filename)
                    search_file(filepath)

        if not file_matches:
            return "Exit code: 1\nNo matches found"

        if self.output_mode == "files_with_matches":
            result = "Exit code: 0\n"
            for filepath in list(file_matches.keys())[:self.max_results]:
                result += f"{filepath}\n"
            return result
        elif self.output_mode == "count":
            result = "Exit code: 0\n"
            for filepath, matches in list(file_matches.items())[:self.max_results]:
                result += f"{filepath}:{len(matches)}\n"
            return result
        else:
            result = "Exit code: 0\n"
            count = 0
            for filepath, matches in file_matches.items():
                for line_num, line in matches:
                    if count >= self.max_results:
                        result += f"\n... truncated at {self.max_results} results"
                        return result
                    result += f"{filepath}:{line_num}:{line}\n"
                    count += 1
            return result

# Alias for tool loading
grep = Grep
```

---

### 2.3 Git Tool

**File**: `src/my_agent_framework/tools/git.py`

```python
import os
import subprocess
from pydantic import Field
from typing import Optional, Literal
from .base import BaseTool

class Git(BaseTool):
    """Execute git operations (read-only for safety).

    Supports status, diff, log, and show commands.
    For write operations like commit/push, use the Bash tool.
    """

    command: Literal["status", "diff", "log", "show", "branch"] = Field(
        ...,
        description="Git command: status, diff, log, show, or branch"
    )
    ref: Optional[str] = Field(
        default="HEAD",
        description="Git reference (commit, branch) for diff/show"
    )
    max_lines: int = Field(
        default=500,
        description="Maximum output lines"
    )

    async def run(self) -> str:
        """Execute the git command"""
        # Check if in git repo
        if not os.path.isdir('.git'):
            return "Error: Not in a git repository"

        try:
            if self.command == "status":
                return await self._git_status()
            elif self.command == "diff":
                return await self._git_diff()
            elif self.command == "log":
                return await self._git_log()
            elif self.command == "show":
                return await self._git_show()
            elif self.command == "branch":
                return await self._git_branch()
            else:
                return f"Error: Unknown command: {self.command}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _run_git(self, args: list) -> tuple:
        """Run a git command and return (returncode, output)"""
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            lines = output.split('\n')
            if len(lines) > self.max_lines:
                output = '\n'.join(lines[:self.max_lines])
                output += f"\n\n... output truncated at {self.max_lines} lines"
            return result.returncode, output
        except subprocess.TimeoutExpired:
            return 124, "Command timed out"
        except Exception as e:
            return 1, str(e)

    async def _git_status(self) -> str:
        """Get git status"""
        code, output = await self._run_git(['status', '--short'])
        return f"Exit code: {code}\n{output}"

    async def _git_diff(self) -> str:
        """Get git diff"""
        code, output = await self._run_git(['diff', self.ref])
        if not output.strip():
            # Try staged diff
            code, output = await self._run_git(['diff', '--staged'])
        return f"Exit code: {code}\n{output}"

    async def _git_log(self) -> str:
        """Get git log"""
        code, output = await self._run_git([
            'log', '--oneline', '-20', '--no-decorate'
        ])
        return f"Exit code: {code}\n{output}"

    async def _git_show(self) -> str:
        """Show commit details"""
        code, output = await self._run_git([
            'show', self.ref, '--stat', '--format=medium'
        ])
        return f"Exit code: {code}\n{output}"

    async def _git_branch(self) -> str:
        """List branches"""
        code, output = await self._run_git(['branch', '-a'])
        return f"Exit code: {code}\n{output}"

# Alias for tool loading
git = Git
```

---

### 2.4 MultiEdit Tool

**File**: `src/my_agent_framework/tools/multi_edit.py`

```python
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseTool
from .read import _global_read_files

class EditOperation(BaseModel):
    """A single edit operation"""
    old_string: str
    new_string: str
    replace_all: bool = False

class MultiEdit(BaseTool):
    """Perform multiple string replacements atomically.

    All edits are validated before any are applied. If any edit
    would fail, none are applied. Edits are applied sequentially.
    """

    file_path: str = Field(
        ...,
        description="The absolute path to the file to edit"
    )
    edits: List[EditOperation] = Field(
        ...,
        description="List of edit operations to perform"
    )

    async def run(self) -> str:
        """Perform all edits atomically"""
        # Validate absolute path
        if not os.path.isabs(self.file_path):
            return f"Error: Path must be absolute: {self.file_path}"

        # Check file exists
        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        abs_path = os.path.abspath(self.file_path)

        # Check precondition: must read first
        file_has_been_read = abs_path in _global_read_files

        if self.context is not None:
            read_files = self.context.get("read_files", set())
            file_has_been_read = file_has_been_read or abs_path in read_files

        if not file_has_been_read:
            return f"Error: You must use the Read tool before editing: {self.file_path}"

        if not self.edits:
            return "Error: No edits provided"

        try:
            # Read current content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            total_replacements = 0

            # Validate all edits first
            for i, edit in enumerate(self.edits):
                if edit.old_string == edit.new_string:
                    return f"Error in edit {i+1}: old_string and new_string must be different"

                occurrences = content.count(edit.old_string)
                if occurrences == 0:
                    return (
                        f"Error in edit {i+1}: old_string not found.\n"
                        f"Looking for: {repr(edit.old_string[:100])}"
                    )

                if occurrences > 1 and not edit.replace_all:
                    return (
                        f"Error in edit {i+1}: old_string appears {occurrences} times. "
                        f"Use replace_all=True or provide more context."
                    )

            # Apply all edits
            for edit in self.edits:
                occurrences = content.count(edit.old_string)
                if edit.replace_all:
                    content = content.replace(edit.old_string, edit.new_string)
                    total_replacements += occurrences
                else:
                    content = content.replace(edit.old_string, edit.new_string, 1)
                    total_replacements += 1

            # Write back
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return (
                f"Successfully applied {len(self.edits)} edits "
                f"({total_replacements} total replacements) to {self.file_path}"
            )

        except Exception as e:
            return f"Error: {str(e)}"

# Alias for tool loading
multi_edit = MultiEdit
```

---

### 2.5 LS Tool

**File**: `src/my_agent_framework/tools/ls.py`

```python
import os
import stat
from datetime import datetime
from pydantic import Field
from typing import Optional, List
from .base import BaseTool

class LS(BaseTool):
    """List directory contents with detailed information.

    Shows file type, permissions, size, and modification date.
    """

    path: str = Field(
        ...,
        description="The absolute path to the directory to list"
    )
    ignore: Optional[List[str]] = Field(
        default=None,
        description="Glob patterns to ignore"
    )

    async def run(self) -> str:
        """List directory contents"""
        import fnmatch

        if not os.path.isabs(self.path):
            return f"Error: Path must be absolute: {self.path}"

        if not os.path.exists(self.path):
            return f"Error: Path does not exist: {self.path}"

        if not os.path.isdir(self.path):
            return f"Error: Path is not a directory: {self.path}"

        try:
            entries = []
            for name in sorted(os.listdir(self.path)):
                # Check ignore patterns
                if self.ignore:
                    skip = False
                    for pattern in self.ignore:
                        if fnmatch.fnmatch(name, pattern):
                            skip = True
                            break
                    if skip:
                        continue

                filepath = os.path.join(self.path, name)
                try:
                    st = os.lstat(filepath)

                    # Determine type
                    if stat.S_ISLNK(st.st_mode):
                        file_type = "LINK"
                    elif stat.S_ISDIR(st.st_mode):
                        file_type = "DIR"
                    elif stat.S_ISREG(st.st_mode):
                        file_type = "FILE"
                    else:
                        file_type = "OTHER"

                    # Format permissions
                    perms = stat.filemode(st.st_mode)[1:]

                    # Format size
                    if file_type == "DIR":
                        size = "-"
                    elif st.st_size < 1024:
                        size = f"{st.st_size}B"
                    elif st.st_size < 1024 * 1024:
                        size = f"{st.st_size / 1024:.1f}KB"
                    else:
                        size = f"{st.st_size / (1024*1024):.1f}MB"

                    # Format date
                    mtime = datetime.fromtimestamp(st.st_mtime)
                    date = mtime.strftime("%Y-%m-%d %H:%M")

                    entries.append({
                        "type": file_type,
                        "perms": perms,
                        "size": size,
                        "date": date,
                        "name": name
                    })
                except:
                    entries.append({
                        "type": "?",
                        "perms": "?",
                        "size": "?",
                        "date": "?",
                        "name": name
                    })

            if not entries:
                return f"Directory is empty: {self.path}"

            # Format output
            result = f"Directory: {self.path}\n\n"
            result += f"{'TYPE':<6} {'PERMISSIONS':<12} {'SIZE':<10} {'MODIFIED':<18} NAME\n"
            result += "-" * 80 + "\n"

            for e in entries:
                result += f"{e['type']:<6} {e['perms']:<12} {e['size']:<10} {e['date']:<18} {e['name']}\n"

            return result

        except PermissionError:
            return f"Error: Permission denied: {self.path}"
        except Exception as e:
            return f"Error: {str(e)}"

# Alias for tool loading
ls = LS
```

---

### 2.6 TodoWrite Tool

**File**: `src/my_agent_framework/tools/todo_write.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from .base import BaseTool

class TodoItem(BaseModel):
    """A single todo item"""
    content: str = Field(..., description="Task description")
    status: Literal["pending", "in_progress", "completed"] = Field(
        ...,
        description="Task status"
    )
    activeForm: str = Field(..., description="Present tense form of the task")
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Task priority"
    )

class TodoWrite(BaseTool):
    """Manage a structured task list for complex workflows.

    Use for tasks requiring 3+ steps. Only ONE task should be
    in_progress at a time. Mark tasks completed immediately
    after finishing.
    """

    todos: List[TodoItem] = Field(
        ...,
        description="The updated todo list"
    )

    async def run(self) -> str:
        """Update the todo list"""
        # Validate: only one in_progress
        in_progress = [t for t in self.todos if t.status == "in_progress"]
        if len(in_progress) > 1:
            return (
                f"Error: Only one task can be in_progress at a time. "
                f"Found {len(in_progress)}: {[t.content for t in in_progress]}"
            )

        # Convert to storage format
        todos_payload = {
            "updated_at": datetime.now().isoformat(),
            "items": [t.model_dump() for t in self.todos]
        }

        # Store in context if available
        if self.context is not None:
            self.context.set("todos", todos_payload)

        # Build summary
        pending = [t for t in self.todos if t.status == "pending"]
        completed = [t for t in self.todos if t.status == "completed"]

        result = f"Todo List Updated ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
        result += f"Summary: total={len(self.todos)}, done={len(completed)}, "
        result += f"in_progress={len(in_progress)}, pending={len(pending)}\n\n"

        if in_progress:
            result += "IN PROGRESS:\n"
            for t in in_progress:
                result += f"  [{t.priority.upper()}] {t.content}\n"
            result += "\n"

        if pending:
            result += "PENDING:\n"
            for t in pending:
                result += f"  [{t.priority.upper()}] {t.content}\n"
            result += "\n"

        if completed:
            result += f"COMPLETED (showing last {min(5, len(completed))}):\n"
            for t in completed[-5:]:
                result += f"  [{t.priority.upper()}] {t.content}\n"

        return result

# Alias for tool loading
todo_write = TodoWrite
```

---

### 2.7 Update Tools Package

**File**: `src/my_agent_framework/tools/__init__.py`

```python
"""
indus-agents Tools Package

Complete toolkit for developer workflows including file operations,
search, version control, and task management.
"""

from .base import BaseTool
from .bash import Bash
from .read import Read
from .write import Write
from .edit import Edit
from .multi_edit import MultiEdit, EditOperation
from .glob import Glob
from .grep import Grep
from .git import Git
from .ls import LS
from .todo_write import TodoWrite, TodoItem

__all__ = [
    # Base
    "BaseTool",

    # File Operations
    "Bash",
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "EditOperation",

    # Discovery
    "Glob",
    "LS",

    # Search
    "Grep",

    # Version Control
    "Git",

    # Task Management
    "TodoWrite",
    "TodoItem",
]
```

---

## Testing Requirements

- Unit tests for each tool
- Integration tests for tool workflows
- Error case coverage
- Performance tests for Glob/Grep on large directories

---

## Acceptance Criteria

- [ ] Glob finds files respecting .gitignore
- [ ] Grep works with ripgrep and Python fallback
- [ ] Git provides safe read-only operations
- [ ] MultiEdit applies changes atomically
- [ ] LS shows detailed file information
- [ ] TodoWrite validates single in_progress task
- [ ] All tools work async and sync
- [ ] 90%+ test coverage

---

## Next Phase

After completing Phase 2, proceed to [Phase 3: Agent System](PHASE3_AGENTS.md) for multi-LLM support and inter-agent communication.
