# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION PATHS
# -------------------------------------------------
"""
Centralized static application paths and filenames.

PURPOSE:
- Define canonical application-owned paths
- Centralize static persistence filenames
- Prevent duplicated filesystem path constants
- Provide configuration-independent infrastructure defaults

ARCHITECTURE ROLE:
This module acts as the single source of truth for static
application paths required before runtime configuration is loaded.

IMPORTANT:
This module contains NO:
- filesystem access
- directory creation
- configuration loading
- runtime state
- user-configurable behavior

Configurable report locations remain owned by AppConfig.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os


# -------------------------------------------------
# APPLICATION LOG PATHS
# -------------------------------------------------
LOGS_DIRECTORY = "logs"

LOG_FILENAME = "smartorg.log"

LOG_FILE_PATH = os.path.join(
    LOGS_DIRECTORY,
    LOG_FILENAME
)