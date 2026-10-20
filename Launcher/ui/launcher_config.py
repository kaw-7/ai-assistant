# -*- coding: utf-8 -*-
"""Look and feel of the launcher window itself.

Colours, the button styles and the font fallbacks are shared with the issue
viewer (``UI/theme.py``); only what is particular to the launcher lives here.
"""

WINDOW_TITLE = "Tool Validation Assistant - Launcher"
APP_NAME = "Validation Assistant"
GEOMETRY = "1280x860"
MIN_WIDTH = 960
MIN_HEIGHT = 620

FONT = "Segoe UI Variable Text"   # falls back to "Segoe UI" when missing
FONT_SIZE = 10

SIDEBAR_WIDTH = 260       # pixels of the module list on the left
TOC_WIDTH = 170           # pixels of the section list next to the form
LABEL_WIDTH = 230         # pixels reserved for the field labels and their hints
FIELD_WIDTH = 320         # minimum pixels of the value widgets
CHOICE_BUTTONS_MAX = 4    # up to this many choices are buttons, more a drop-down

# the dark side bar
COLOR_SIDEBAR = "#1C232D"
COLOR_SIDEBAR_HOVER = "#242D39"
COLOR_SIDEBAR_SELECTED = "#2A3442"
COLOR_SIDEBAR_LINE = "#3A4658"
COLOR_SIDEBAR_TEXT = "#E6E9EE"
COLOR_SIDEBAR_MUTED = "#8A94A3"

COLOR_CONSOLE_BG = "#161B22"
COLOR_CONSOLE_BAR = "#1C232D"
COLOR_CONSOLE_FG = "#D5DBE3"
COLOR_CONSOLE_INFO = "#7FB2FF"
COLOR_CONSOLE_OK = "#7DDC7D"
COLOR_CONSOLE_ERROR = "#FF8A8A"

CONSOLE_HEIGHT = 8        # text lines
FORM_SHARE = 0.78         # part of the height the form gets at start, the output the rest
CONSOLE_MAX_LINES = 5000  # older output is dropped

QUEUE_POLL_MS = 80        # how often the output queue is drained

STATE_IDLE = "Idle"
STATE_RUNNING = "Running"
