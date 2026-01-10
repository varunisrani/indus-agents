"""
Module entrypoint so the CLI can be run without installing the console script.

Examples:
  python -m indusagi --help
  python -m indusagi agency-demo --model glm-4.7
"""

from __future__ import annotations

from indusagi.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()

