# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION ENTRY POINT
# -------------------------------------------------
"""
This module serves as the application entry point and
composition root.

Responsibilities:
- Consume parsed CLI arguments
- Load application configuration
- Build the runtime execution context
- Inject application dependencies
- Route supported commands to application handlers
- Emit application startup and execution-context logs

Architecture Role:
This file intentionally contains NO logic related to:
- CLI parser construction
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
- persistence cleanup

Instead, it functions as the composition root responsible
for wiring together the application's handlers and subsystems.

CLI parsing is delegated to cli/parser.py.
Application workflows are delegated to handlers.py.

Application Flow:
CLI parsing
→ configuration loading
→ runtime context construction
→ dependency injection
→ command routing
→ application handler
→ subsystem execution

Subsystems:
- cli:
    Command-line parsing and argument validation
- discovery:
    Filesystem discovery and classification
- execution:
    Planning and filesystem mutations
- rollback:
    Rollback workflow coordination
- reporting:
    Report generation, persistence, loading, history,
    and presentation
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
    handle_move,
    handle_report,
    handle_rollback,
)

from cli.parser import parse_args

from utils.config_loader import get_config
from utils.logger import log_info

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
)

from core.metadata import APP_BANNER

from core.paths import (
    LOG_FILENAME,
    LOGS_DIRECTORY,
)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main() -> None:
    """
    CLI entry point.
    """

    args = parse_args()

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

    reports_directory = config.reports_directory

    execution_reports_directory = (
        config.execution_reports_directory
    )

    rollback_reports_directory = (
        config.rollback_reports_directory
    )

    # -------------------------------------------------
    # STARTUP
    # -------------------------------------------------
    log_info(
        f"{APP_START} | "
        f"banner={APP_BANNER}"
    )

    # -------------------------------------------------
    # EXECUTION CONTEXT
    # -------------------------------------------------
    task = args.task

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
            folder_prefix,
            reports_directory,
            execution_reports_directory
        )

    elif task == "report":

        handle_report(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            report_reference
        )

    elif task == "rollback":

        handle_rollback(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            dry_run
        )

    elif task == "cleanup":

        handle_cleanup(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            LOGS_DIRECTORY,
            LOG_FILENAME,
            cleanup_resource,
            cleanup_target
        )


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()