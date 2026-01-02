"""Directory listing tool."""

from typing import Optional, ClassVar, List
from pydantic import Field
from ..base import BaseTool
import os
import stat
from datetime import datetime


class LS(BaseTool):
    """
    List directory contents with detailed information.

    Provides file listings similar to Unix 'ls' command with options
    for showing hidden files, long format, and more.

    Example:
        >>> ls = LS(path="./src", all_files=True)
        >>> print(ls.execute())
    """

    name: ClassVar[str] = "ls"
    description: ClassVar[str] = """List directory contents with details.
    Shows files and directories with optional size, permissions, and modification time."""

    path: str = Field(
        default=".",
        description="Directory path to list (defaults to current directory)"
    )
    all_files: bool = Field(
        default=False,
        description="Include hidden files (starting with .)"
    )
    long_format: bool = Field(
        default=True,
        description="Use long listing format with details"
    )
    human_readable: bool = Field(
        default=True,
        description="Show sizes in human-readable format (KB, MB, GB)"
    )
    sort_by: str = Field(
        default="name",
        description="Sort by: name, size, modified, type"
    )
    reverse: bool = Field(
        default=False,
        description="Reverse the sort order"
    )
    recursive: bool = Field(
        default=False,
        description="List directories recursively"
    )
    max_depth: int = Field(
        default=2,
        description="Maximum depth for recursive listing"
    )

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        if not self.human_readable:
            return str(size)

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:7.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def _format_mode(self, mode: int) -> str:
        """Format file mode as permission string."""
        is_dir = 'd' if stat.S_ISDIR(mode) else '-'
        perms = ''
        for who in ['USR', 'GRP', 'OTH']:
            for what in ['R', 'W', 'X']:
                perm = getattr(stat, f'S_I{what}{who}')
                perms += what.lower() if mode & perm else '-'
        return is_dir + perms

    def _list_directory(self, path: str, depth: int = 0) -> List[str]:
        """List a single directory."""
        lines = []

        try:
            entries = os.listdir(path)
        except PermissionError:
            return [f"Permission denied: {path}"]
        except FileNotFoundError:
            return [f"Directory not found: {path}"]

        # Filter hidden files
        if not self.all_files:
            entries = [e for e in entries if not e.startswith('.')]

        # Get full info for sorting and display
        entry_info = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            try:
                stat_info = os.stat(full_path)
                entry_info.append({
                    'name': entry,
                    'path': full_path,
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime,
                    'mode': stat_info.st_mode,
                    'is_dir': os.path.isdir(full_path)
                })
            except (OSError, PermissionError):
                entry_info.append({
                    'name': entry,
                    'path': full_path,
                    'size': 0,
                    'modified': 0,
                    'mode': 0,
                    'is_dir': False
                })

        # Sort entries
        sort_key = {
            'name': lambda x: x['name'].lower(),
            'size': lambda x: x['size'],
            'modified': lambda x: x['modified'],
            'type': lambda x: (not x['is_dir'], x['name'].lower())
        }.get(self.sort_by, lambda x: x['name'].lower())

        entry_info.sort(key=sort_key, reverse=self.reverse)

        # Format output
        indent = "  " * depth
        for info in entry_info:
            if self.long_format:
                mode_str = self._format_mode(info['mode'])
                size_str = self._format_size(info['size'])
                time_str = datetime.fromtimestamp(info['modified']).strftime('%Y-%m-%d %H:%M')
                name = info['name'] + ('/' if info['is_dir'] else '')
                lines.append(f"{indent}{mode_str} {size_str} {time_str} {name}")
            else:
                name = info['name'] + ('/' if info['is_dir'] else '')
                lines.append(f"{indent}{name}")

            # Recursive listing
            if self.recursive and info['is_dir'] and depth < self.max_depth:
                lines.extend(self._list_directory(info['path'], depth + 1))

        return lines

    def execute(self) -> str:
        """
        Execute the directory listing.

        Returns:
            Formatted directory listing or error message
        """
        path = os.path.expanduser(self.path)

        if not os.path.exists(path):
            return f"Error: Path does not exist: {path}"

        if not os.path.isdir(path):
            # Single file - show its info
            try:
                stat_info = os.stat(path)
                if self.long_format:
                    mode_str = self._format_mode(stat_info.st_mode)
                    size_str = self._format_size(stat_info.st_size)
                    time_str = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    return f"{mode_str} {size_str} {time_str} {os.path.basename(path)}"
                return os.path.basename(path)
            except Exception as e:
                return f"Error: {str(e)}"

        lines = self._list_directory(path)

        if not lines:
            return "(empty directory)"

        return "\n".join(lines)


class Tree(BaseTool):
    """
    Display directory tree structure.

    Shows a visual tree representation of directory structure.
    """

    name: ClassVar[str] = "tree"
    description: ClassVar[str] = """Display directory tree structure.
    Shows a visual tree representation similar to the 'tree' command."""

    path: str = Field(
        default=".",
        description="Root directory for tree"
    )
    max_depth: int = Field(
        default=3,
        description="Maximum depth to display"
    )
    show_hidden: bool = Field(
        default=False,
        description="Show hidden files and directories"
    )
    dirs_only: bool = Field(
        default=False,
        description="Only show directories, not files"
    )

    def _build_tree(self, path: str, prefix: str = "", depth: int = 0) -> List[str]:
        """Build tree representation."""
        lines = []

        if depth > self.max_depth:
            return lines

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return [f"{prefix}[Permission denied]"]

        if not self.show_hidden:
            entries = [e for e in entries if not e.startswith('.')]

        if self.dirs_only:
            entries = [e for e in entries if os.path.isdir(os.path.join(path, e))]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)

            display_name = entry + "/" if is_dir else entry
            lines.append(f"{prefix}{connector}{display_name}")

            if is_dir:
                extension = "    " if is_last else "│   "
                lines.extend(self._build_tree(full_path, prefix + extension, depth + 1))

        return lines

    def execute(self) -> str:
        """Execute tree command."""
        path = os.path.expanduser(self.path)

        if not os.path.exists(path):
            return f"Error: Path does not exist: {path}"

        if not os.path.isdir(path):
            return f"Error: Not a directory: {path}"

        lines = [path]
        lines.extend(self._build_tree(path))

        return "\n".join(lines)
