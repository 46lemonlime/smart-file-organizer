# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION ENTRY POINT
# -------------------------------------------------
"""
This module serves as the application entry point and
composition root.

Responsibilities:
- Consume parsed CLI arguments
- Verify application initialization state
- Load application configuration
- Resolve runtime execution values
- Inject application dependencies
- Route supported commands to application handlers
- Emit application startup and execution-context logs

Architecture Role:
This file intentionally contains NO logic related to:
- CLI parser construction
- application directory creation
- default configuration generation
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- rollback implementation
- report generation
- report persistence
- report reconstruction
- report rendering
- report history construction
- report history filtering
- persistence cleanup

Instead, it functions as the composition root responsible
for wiring together the application's handlers and subsystems.

CLI parsing is delegated to cli/parser.py.
Application workflows are delegated to the handlers package.

Application Flow:
CLI parsing
→ initialization-state verification
→ configuration loading
→ runtime context construction
→ dependency injection
→ command routing
→ application handler
→ subsystem execution

IMPORTANT:
Every command other than `init` requires an initialized
application directory. Commands issued before initialization
are rejected with user-facing guidance instead of routing to
their handler.

Subsystems:
- cli:
    Command-line parsing and argument validation
- bootstrap:
    Application directory and configuration initialization
- discovery:
    Filesystem discovery and classification
- execution:
    Planning and filesystem mutations
- rollback:
    Rollback workflow coordination
- reporting:
    Report generation, persistence, loading, history,
    filtering, and presentation
- cleanup:
    Report deletion and application log cleanup

Design Principles:
- minimal orchestration
- separation of concerns
- contract-first architecture
- deterministic application flow
- centralized dependency composition
- explicit dependency injection
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from handlers import (
    handle_cleanup,
    handle_init,
    handle_move,
    handle_report,
    handle_rollback,
)

from cli.parser import parse_args

from tasks.bootstrap import is_app_initialized

from utils.config_loader import get_config
from utils.logger import log_info

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
)

from core.metadata import APP_BANNER

from core.paths import LOG_FILE_PATH


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main() -> None:
    """
    CLI entry point.
    """

    args = parse_args()

    # -------------------------------------------------
    # STARTUP
    # -------------------------------------------------
    log_info(
        f"{APP_START} | "
        f"banner={APP_BANNER}"
    )

    task = args.task

    # -------------------------------------------------
    # INITIALIZATION GUARD
    # -------------------------------------------------
    if task != "init" and not is_app_initialized():

        print()
        print("SmartOrg is not initialized.")
        print()
        print("Run:")
        print()
        print("    smartorg init")
        print()

        return

    # -------------------------------------------------
    # INIT ROUTING
    # -------------------------------------------------
    if task == "init":

        handle_init()

        return

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    config = get_config()

    dry_run = getattr(
        args,
        "dry_run",
        False
    ) or config.dry_run

    folder_prefix = config.folder_prefix

    # -------------------------------------------------
    # EXECUTION CONTEXT
    # -------------------------------------------------
    path = getattr(
        args,
        "path",
        None
    )

    report_reference = getattr(
        args,
        "reference",
        None
    )

    report_scope = getattr(
        args,
        "report_scope",
        None
    )

    cleanup_resource = getattr(
        args,
        "cleanup_resource",
        None
    )

    cleanup_target = getattr(
        args,
        "cleanup_target",
        None
    )

    log_info(
        f"{EXECUTION_CONTEXT} | "
        f"task={task} "
        f"path={path} "
        f"report_reference={report_reference} "
        f"report_scope={report_scope} "
        f"cleanup_resource={cleanup_resource} "
        f"cleanup_target={cleanup_target} "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # TASK ROUTING
    # -------------------------------------------------
    if task == "move":

        handle_move(
            path,
            dry_run,
            folder_prefix
        )

    elif task == "report":

        handle_report(
            report_reference,
            report_scope
        )

    elif task == "rollback":

        handle_rollback(
            dry_run
        )

    elif task == "cleanup":

        handle_cleanup(
            LOG_FILE_PATH,
            cleanup_resource,
            cleanup_target
        )

    else:
        raise ValueError(f"Unsupported task: {task}")


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()