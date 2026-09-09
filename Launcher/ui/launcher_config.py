# -*- coding: utf-8 -*-
"""Look and feel of the launcher window itself."""

WINDOW_TITLE = "Tool Validation Assistant - Launcher"
GEOMETRY = "1180x820"
MIN_WIDTH = 900
MIN_HEIGHT = 600

PADX = 6
PADY = 4
SECTION_PADX = 8
SECTION_PADY = 6

FONT = "Segoe UI"
FONT_SIZE = 9
TITLE_FONT_SIZE = 12
MONO_FONT = "Consolas"
MONO_FONT_SIZE = 9

LABEL_WIDTH = 34          # characters reserved for the field labels
CHECK_WIDTH = 24          # pixels reserved for the override tick
FIELD_WIDTH = 380         # pixels reserved for the value widgets
MODULE_LIST_WIDTH = 32    # characters of the module list

COLOR_HINT = "#666666"
COLOR_DERIVED = "#f2f2f2"
COLOR_CONSOLE_BG = "#1e1e1e"
COLOR_CONSOLE_FG = "#e8e8e8"
COLOR_CONSOLE_INFO = "#7fb2ff"
COLOR_CONSOLE_OK = "#7ddc7d"
COLOR_CONSOLE_ERROR = "#ff8a8a"

CONSOLE_HEIGHT = 14       # text lines
CONSOLE_MAX_LINES = 5000  # older output is dropped

QUEUE_POLL_MS = 80        # how often the output queue is drained

STATE_IDLE = "Idle"
STATE_RUNNING = "Running"

WRAP_LENGTH = 620         # wrapping of the description texts
