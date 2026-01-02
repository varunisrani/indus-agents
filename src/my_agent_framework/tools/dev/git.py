"""Git operations tool for version control."""

from typing import Optional, ClassVar, List
from pydantic import Field
from ..base import BaseTool
import subprocess
import os


class Git(BaseTool):
    """
    Execute git commands for version control operations.

    Supports common git operations like status, add, commit, push, pull,
    branch management, diff, log, and more.

    Example:
        >>> git = Git(command="status")
        >>> print(git.execute())

        >>> git = Git(command="commit", message="Add new feature")
        >>> print(git.execute())
    """

    name: ClassVar[str] = "git"
    description: ClassVar[str] = """Execute git commands for version control.
    Supports: status, add, commit, push, pull, branch, checkout, diff, log, clone, fetch, merge, stash.
    Use for version control operations in the repository."""

    command: str = Field(
        ...,
        description="Git subcommand (status, add, commit, push, pull, branch, checkout, diff, log, clone, fetch, merge, stash)"
    )
    args: Optional[str] = Field(
        default=None,
        description="Additional arguments for the git command (e.g., file paths, branch names)"
    )
    message: Optional[str] = Field(
        default=None,
        description="Commit message (required for commit command)"
    )
    working_dir: Optional[str] = Field(
        default=None,
        description="Working directory for git operations (defaults to current directory)"
    )

    # Commands that are considered safe (read-only)
    SAFE_COMMANDS: ClassVar[List[str]] = [
        "status", "log", "diff", "branch", "show", "ls-files",
        "remote", "fetch", "stash list"
    ]

    # Commands that modify state and need caution
    MODIFY_COMMANDS: ClassVar[List[str]] = [
        "add", "commit", "push", "pull", "checkout", "merge",
        "reset", "stash", "clone", "rebase"
    ]

    def execute(self) -> str:
        """
        Execute the git command.

        Returns:
            Output from git command or error message
        """
        # Validate command
        valid_commands = self.SAFE_COMMANDS + self.MODIFY_COMMANDS
        base_cmd = self.command.split()[0] if self.command else ""

        if base_cmd not in valid_commands:
            return f"Error: Unsupported git command '{base_cmd}'. Supported: {', '.join(valid_commands)}"

        # Build command list
        cmd = ["git", self.command]

        if self.args:
            # Split args but preserve quoted strings
            cmd.extend(self.args.split())

        # Handle commit message
        if self.command == "commit":
            if not self.message:
                return "Error: Commit message is required for git commit"
            cmd.extend(["-m", self.message])

        # Set working directory
        cwd = self.working_dir or os.getcwd()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd
            )

            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.stderr else ""

            if result.returncode == 0:
                return output or "Command completed successfully (no output)"
            else:
                # Some git commands output to stderr even on success
                if output:
                    return f"Exit code: {result.returncode}\n{output}\n{error}".strip()
                return f"Error (exit code {result.returncode}):\n{error or 'Unknown error'}"

        except subprocess.TimeoutExpired:
            return "Error: Git command timed out after 60 seconds"
        except FileNotFoundError:
            return "Error: Git is not installed or not in PATH"
        except Exception as e:
            return f"Error executing git command: {str(e)}"


class GitStatus(BaseTool):
    """Quick git status check."""

    name: ClassVar[str] = "git_status"
    description: ClassVar[str] = "Get quick git status of the repository."

    path: Optional[str] = Field(
        default=None,
        description="Path to check status for (defaults to current directory)"
    )

    def execute(self) -> str:
        """Execute git status."""
        cwd = self.path or os.getcwd()
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd
            )
            if result.returncode == 0:
                status = result.stdout.strip()
                return status if status else "Working tree clean"
            return f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitDiff(BaseTool):
    """Show git diff for changes."""

    name: ClassVar[str] = "git_diff"
    description: ClassVar[str] = "Show changes in the repository (staged or unstaged)."

    staged: bool = Field(
        default=False,
        description="Show staged changes (--cached)"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Specific file to diff"
    )

    def execute(self) -> str:
        """Execute git diff."""
        cmd = ["git", "diff"]
        if self.staged:
            cmd.append("--cached")
        if self.file_path:
            cmd.append(self.file_path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            diff = result.stdout.strip()
            return diff if diff else "No changes"
        except Exception as e:
            return f"Error: {str(e)}"
