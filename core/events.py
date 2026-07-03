"""
Smart File Organizer - Event Definitions

This module centralizes structured application event names
used across the Smart File Organizer pipeline.

PURPOSE:
- standardize event naming
- eliminate duplicated event strings
- improve logging consistency
- centralize observability semantics
- reduce logging drift across modules

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- structured event identifiers
- logging event semantics
- pipeline observability consistency

IMPORTANT:
Events define WHAT happened inside the system,
not HOW logging is implemented.

This module intentionally contains:
- no logging logic
- no formatting logic
- no business logic
- no filesystem logic

DESIGN PRINCIPLES:
- deterministic event naming
- centralized semantic ownership
- stable observability contracts
- low coupling across modules
- machine-readable consistency

EXAMPLE:
EVENT_MOVE_COMPLETED = "move_completed"
EVENT_PLAN_FAILED = "plan_failed"
"""

# -------------------------------------------------
# APPLICATION EVENTS
# -------------------------------------------------
APP_START = "app_start"
APP_COMPLETE = "app_complete"

# -------------------------------------------------
# CONTEXT EVENTS
# -------------------------------------------------
EXECUTION_CONTEXT = "execution_context"
PATH_INVALID = "path_invalid"
TASK_UNKNOWN = "task_unknown"

# -------------------------------------------------
# SCANNER EVENTS
# -------------------------------------------------
SCAN_START = "scan_start"
SCAN_ITEMS = "scan_items"
SCAN_COMPLETE = "scan_complete"
SCAN_FAILED = "scan_failed"

# -------------------------------------------------
# DISCOVERY EVENTS
# -------------------------------------------------
DISCOVERY_START = "discovery_start"
DISCOVERY_COMPLETE = "discovery_complete"
DISCOVERY_FAILED = "discovery_failed"
DISCOVERY_SKIP = "discovery_skip"
DISCOVERY_FALLBACK = "discovery_fallback"

# -------------------------------------------------
# PLANNING EVENTS
# -------------------------------------------------
PLAN_START = "plan_start"
PLAN_READY = "plan_ready"
PLAN_FAILED = "plan_failed"
PLAN_BUILD_START = "plan_build_start"
PLAN_BUILD_COMPLETE = "plan_build_complete"

# -------------------------------------------------
# EXECUTION EVENTS
# -------------------------------------------------
MOVE_START = "move_start"
MOVE_COMPLETE = "move_complete"
MOVE_SUMMARY = "move_summary"
MOVE_FAILED = "move_failed"
MOVE_SKIP = "move_skip"

# -------------------------------------------------
# FILE EVENTS
# -------------------------------------------------
FILE_MOVED = "file_moved"
FILE_MOVE_SIMULATION = "file_move_simulation"

# -------------------------------------------------
# FOLDER EVENTS
# -------------------------------------------------
FOLDER_CREATED = "folder_created"
FOLDER_CREATE_FAILED = "folder_create_failed"
FOLDER_CREATE_SIMULATION = "folder_create_simulation"

# -------------------------------------------------
# SUMMARY EVENTS
# -------------------------------------------------
MOVE_SUMMARY_FAILED = "move_summary_failed"

# -------------------------------------------------
# REPORTING EVENTS
# -------------------------------------------------
REPORT_START = "report_start"
REPORT_COMPLETE = "report_complete"

#------------------------------------------------
# CONFIGURATION EVENTS
#------------------------------------------------
CONFIG_GET_START = "config_get_start"
CONFIG_GET_COMPLETE = "config_get_complete"

CONFIG_LOAD_START = "config_load_start"
CONFIG_LOAD_SUCCESS = "config_load_success"
CONFIG_LOAD_FAILED = "config_load_failed"

CONFIG_INVALID = "config_invalid"
CONFIG_WARNING = "config_warning"
CONFIG_FALLBACK_USED = "config_fallback_used"

# -------------------------------------------------
# VALIDATION EVENTS
# -------------------------------------------------
INVALID_PLAN_CONTRACT = "invalid_plan_contract"
INVALID_OPERATION_CONTRACT = "invalid_operation_contract"