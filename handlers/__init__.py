# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION HANDLERS
# -------------------------------------------------
"""
Public exports for Smart File Organizer application handlers.

PURPOSE:
- Expose application workflow handlers through a stable API
- Hide the internal organization of handler modules
- Preserve simple imports from the application entry point

ARCHITECTURE ROLE:
This package represents the application orchestration layer
between main.py and specialized task subsystems.

Application modules should import handlers directly from:

    handlers

rather than individual handler modules.

Example:

    from handlers import (
        handle_cleanup,
        handle_init,
        handle_move,
        handle_report,
        handle_rollback,
    )
"""

from .cleanup import handle_cleanup
from .init import handle_init
from .move import handle_move
from .report import handle_report
from .rollback import handle_rollback