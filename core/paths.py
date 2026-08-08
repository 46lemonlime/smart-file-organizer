# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION PATHS
# -------------------------------------------------
"""
Centralized application-owned paths and filenames.

PURPOSE:
- Define the canonical SmartOrg application directory
- Define persistent configuration, log, and report paths
- Centralize application-owned filesystem constants
- Prevent duplicated path construction across modules
- Provide configuration-independent infrastructure defaults

ARCHITECTURE ROLE:
This module acts as the single source of truth for application-owned
paths required before runtime configuration is loaded.

All persistent SmartOrg data is stored under:

    ~/smartorg/

IMPORTANT:
This module contains NO:
- filesystem reads or writes
- directory creation
- configuration loading
- mutable runtime state
- user-configurable behavior

The paths declared here may not exist until the application is
initialized through the `smartorg init` command.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from pathlib import Path


# -------------------------------------------------
# APPLICATION DIRECTORY
# -------------------------------------------------
APP_DIRECTORY_NAME = "smartorg"

APP_DIRECTORY = Path.home() / APP_DIRECTORY_NAME


# -------------------------------------------------
# CONFIGURATION PATHS
# -------------------------------------------------
CONFIG_FILENAME = "config.yaml"

CONFIG_FILE_PATH = APP_DIRECTORY / CONFIG_FILENAME


# -------------------------------------------------
# LOG PATHS
# -------------------------------------------------
LOGS_DIRECTORY_NAME = "logs"

LOGS_DIRECTORY = APP_DIRECTORY / LOGS_DIRECTORY_NAME

LOG_FILENAME = "smartorg.log"

LOG_FILE_PATH = LOGS_DIRECTORY / LOG_FILENAME


# -------------------------------------------------
# REPORT PATHS
# -------------------------------------------------
REPORTS_DIRECTORY_NAME = "reports"

REPORTS_DIRECTORY = APP_DIRECTORY / REPORTS_DIRECTORY_NAME


# -------------------------------------------------
# EXECUTION REPORT PATHS
# -------------------------------------------------
EXECUTION_REPORTS_DIRECTORY_NAME = "executions"

EXECUTION_REPORTS_DIRECTORY = (
    REPORTS_DIRECTORY
    / EXECUTION_REPORTS_DIRECTORY_NAME
)


# -------------------------------------------------
# ROLLBACK REPORT PATHS
# -------------------------------------------------
ROLLBACK_REPORTS_DIRECTORY_NAME = "rollbacks"

ROLLBACK_REPORTS_DIRECTORY = (
    REPORTS_DIRECTORY
    / ROLLBACK_REPORTS_DIRECTORY_NAME
)