# -------------------------------------------------
# SMART FILE ORGANIZER - INIT HANDLER
# -------------------------------------------------
"""
Coordinates application initialization.

Responsibilities:
- Coordinate application directory creation
- Coordinate default configuration creation
- Provide user-facing initialization feedback
- Emit initialization workflow observability events

Architecture Role:
This module defines the application-level init workflow.

It composes specialized bootstrap subsystem functions without
implementing directory creation or configuration generation
directly.

Workflow:
init command
→ initialization-state check
→ directory creation
→ default configuration creation
→ user feedback

Design Principles:
- application-level orchestration
- explicit dependency injection
- deterministic workflow coordination
- subsystem ownership preservation
- minimal business logic

IMPORTANT:
Reinitializing an already-initialized installation is safe:
existing directories and configuration are left untouched.

This module coordinates initialization only. It does NOT:
- verify initialization state using its own logic
- create directories or configuration files directly
- load or validate application configuration
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.paths import APP_DIRECTORY

from core.events import (
    INIT_COMPLETE,
    INIT_SKIPPED,
    INIT_START,
)

from tasks.bootstrap import (
    create_app_directories,
    create_default_config,
    is_app_initialized,
)

from utils.logger import log_info


# -------------------------------------------------
# PUBLIC: Init handler
# -------------------------------------------------
def handle_init() -> None:
    """
    Initializes the SmartOrg application directory structure
    and default configuration.

    If the application is already initialized, existing
    directories and configuration are left untouched.
    """

    log_info(
        f"{INIT_START}"
    )

    if is_app_initialized():

        log_info(
            f"{INIT_SKIPPED} | "
            f"reason=already_initialized "
            f"path={APP_DIRECTORY}"
        )

        print()
        print("SmartOrg is already initialized.")
        print(f"Location: {APP_DIRECTORY}")
        print()

        return

    create_app_directories()

    config_created = create_default_config()

    log_info(
        f"{INIT_COMPLETE} | "
        f"path={APP_DIRECTORY} "
        f"config_created={config_created}"
    )

    print()
    print("SmartOrg initialized successfully.")
    print(f"Location: {APP_DIRECTORY}")
    print()
    print("You can now run:")
    print()
    print("    smartorg move <path>")
    print()