# -------------------------------------------------
# APPLICATION INITIALIZATION VERIFIER
# -------------------------------------------------
"""
Smart File Organizer - Initialization Verifier

Responsibilities:
- Determine whether the application has been initialized

Architecture Role:
This module owns the minimal readiness check used by the
application entry point before routing non-init commands.

It intentionally contains NO logic related to:
- directory creation
- configuration generation
- configuration loading
- command-line behavior

Design Principles:
- minimal readiness criteria
- read-only filesystem checks
- no mutation

IMPORTANT:
Report and log subdirectories are not part of the readiness
criteria. They are fully owned and created by `smartorg init`
and are never created lazily by other commands.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.paths import APP_DIRECTORY, CONFIG_FILE_PATH


# -------------------------------------------------
# PUBLIC: Is app initialized
# -------------------------------------------------
def is_app_initialized() -> bool:
    """
    Checks whether the application has been initialized.

    Initialization is considered complete when the application
    directory and configuration file both exist.

    RETURNS:
        bool
    """

    return (
        APP_DIRECTORY.is_dir()
        and CONFIG_FILE_PATH.is_file()
    )