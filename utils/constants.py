# -------------------------------------------------
# PROJECT CONSTANTS
# -------------------------------------------------
"""
Centralized constants for Smart File Organizer.

PURPOSE:
- Single source of truth (SSOT)
- Avoid version drift across modules
- Reduce magic strings in codebase
"""

# -------------------------------------------------
# PROJECT VERSION
# -------------------------------------------------
PROJECT_NAME = "Smart File Organizer"
PROJECT_VERSION = "0.7.0"

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
LOG_FILE_NAME = "smartorg.log"
LOG_DIR = "logs"

# -------------------------------------------------
# CLI
# -------------------------------------------------
DEFAULT_FOLDER_PREFIX = "smartorg"

# -------------------------------------------------
# TASKS
# -------------------------------------------------
TASK_MOVE = "move"
TASK_REPORT = "report"

# -------------------------------------------------
# MODULE IDENTIFIERS (optional future logging consistency)
# -------------------------------------------------
MODULE_MAIN = "MAIN"
MODULE_SCANNER = "FILE_SCANNER"
MODULE_MOVER = "FILE_MOVER"
MODULE_PLANNER = "EXECUTION_PLANNER"
MODULE_CONFIG = "CONFIG_LOADER"