# -------------------------------------------------
# SMART FILE ORGANIZER - BOOTSTRAP SUBSYSTEM
# -------------------------------------------------
"""
Public exports for the application bootstrap subsystem.

PURPOSE:
- Expose application initialization functions through a
  stable API
- Hide the internal organization of bootstrap modules

ARCHITECTURE ROLE:
This package owns one-time application setup: creating
application-owned directories, generating a default
configuration file, and verifying whether the application has
already been initialized.

Application modules should import bootstrap functions directly
from:

    tasks.bootstrap

rather than individual bootstrap modules.

Example:

    from tasks.bootstrap import (
        create_app_directories,
        create_default_config,
        is_app_initialized,
    )
"""

from .initializer import (
    create_app_directories,
    create_default_config,
)

from .verifier import is_app_initialized