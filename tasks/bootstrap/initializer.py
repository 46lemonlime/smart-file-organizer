# -------------------------------------------------
# APPLICATION INITIALIZER
# -------------------------------------------------
"""
Smart File Organizer - Application Initializer

Responsibilities:
- Create application-owned directories
- Create a default configuration file

Architecture Role:
This module owns the one-time filesystem setup required before
the application can operate. It is invoked exclusively through
`smartorg init`.

It intentionally contains NO logic related to:
- configuration loading
- configuration validation
- initialization-state verification
- command-line behavior

Design Principles:
- idempotent directory creation
- never overwrites an existing configuration file
- application-owned paths only (core.paths)

IMPORTANT:
This module does not verify whether the application is already
initialized. That responsibility belongs to
tasks.bootstrap.verifier. Functions here are safe to call
regardless of current initialization state.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.paths import (
    APP_DIRECTORY,
    CONFIG_FILE_PATH,
    EXECUTION_REPORTS_DIRECTORY,
    LOGS_DIRECTORY,
    REPORTS_DIRECTORY,
    ROLLBACK_REPORTS_DIRECTORY,
)


# -------------------------------------------------
# DEFAULT CONFIGURATION TEMPLATE
# -------------------------------------------------
DEFAULT_CONFIG_TEMPLATE = """\
# ----------------------------------------
# GENERAL SETTINGS
# ----------------------------------------
folder_prefix: smartorg

ignore_hidden_files: true
ignore_symlinks: true

# ----------------------------------------
# EXECUTION SETTINGS
# ----------------------------------------
dry_run: false

# ----------------------------------------
# CLASSIFICATION RULES
# ----------------------------------------
categories:

  images:
    description: "Image and graphic files"
    extensions:
      - .png
      - .jpg
      - .jpeg
      - .gif
      - .webp

  documents:
    description: "Text documents, PDFs, and archives"
    extensions:
      - .pdf
      - .docx
      - .txt
      - .md
      - .zip

  videos:
    description: "Video media files"
    extensions:
      - .mp4
      - .mov
      - .avi
      - .mkv
"""


# -------------------------------------------------
# PUBLIC: Create app directories
# -------------------------------------------------
def create_app_directories() -> None:
    """
    Creates all application-owned directories.

    Safe to call on an already-initialized installation:
    existing directories are left untouched.
    """

    for directory in (
        APP_DIRECTORY,
        LOGS_DIRECTORY,
        REPORTS_DIRECTORY,
        EXECUTION_REPORTS_DIRECTORY,
        ROLLBACK_REPORTS_DIRECTORY,
    ):

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


# -------------------------------------------------
# PUBLIC: Create default config
# -------------------------------------------------
def create_default_config() -> bool:
    """
    Creates a default configuration file.

    An existing configuration file is never overwritten, to
    avoid discarding user customization.

    RETURNS:
        bool:
            True if a new configuration file was created.
            False if a configuration file already existed.
    """

    if CONFIG_FILE_PATH.is_file():
        return False

    CONFIG_FILE_PATH.write_text(
        DEFAULT_CONFIG_TEMPLATE,
        encoding="utf-8",
    )

    return True