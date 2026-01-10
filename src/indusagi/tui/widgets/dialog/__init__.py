"""
Dialog widgets for the TUI.

Modal dialogs for various interactions:
- CommandPalette: Quick command access
- ModelSelect: Model/provider selection
- SessionList: Session switching
- SettingsDialog: App settings
"""

from indusagi.tui.widgets.dialog.base import BaseDialog
from indusagi.tui.widgets.dialog.command_palette import CommandPalette
from indusagi.tui.widgets.dialog.settings import SettingsDialog

__all__ = [
    "BaseDialog",
    "CommandPalette",
    "SettingsDialog",
]
