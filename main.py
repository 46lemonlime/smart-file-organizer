# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION ENTRY POINT
# -------------------------------------------------
"""
This module serves as the application entry point and
top-level orchestration layer.

Responsibilities:
- Consume parsed CLI arguments
- Load application configuration
- Validate execution context
- Route supported tasks
- Coordinate high-level application flow
- Inject runtime dependencies into subsystems
- Route report history actions and references
- Route individual and scoped report deletion requests
- Route application log cleanup requests

Architecture Role:
This file intentionally contains NO logic related to:
- CLI parser construction
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- rollback implementation
- report persistence implementation
- report reconstruction implementation
- report rendering implementation
- report history construction
- report deletion implementation
- log cleanup implementation

Instead, it functions as the composition root responsible
for wiring together the application's subsystems.

CLI parsing is delegated to cli/parser.py.

Application Flow:
CLI parsing
→ configuration loading
→ dependency injection
→ execution context validation
→ task routing
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
    cleanup, and presentation

Design Principles:
- minimal orchestration
- separation of concerns
- contract-first architecture
- deterministic application flow
- centralized dependency composition
- explicit dependency injection

Failure Contract:
- validates execution context before routing
- prevents invalid task execution
- handles unavailable persisted reports safely
- handles unavailable application logs safely
- provides actionable CLI feedback
- delegates subsystem failures to their owners

Observability:
Structured logs are emitted throughout execution to provide:
- application lifecycle visibility
- execution context diagnostics
- task routing traceability
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import modules from the project
from tasks.execution.planner import build_execution_plan
from tasks.discovery.coordinator import discover_files
from tasks.execution.mover import move_files

from handlers import (
    handle_move,
    handle_report,
    handle_rollback
)

from cli.parser import parse_args

from utils.logger import log_info
from utils.config_loader import get_config

from core.metadata import (
    APP_BANNER
)

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
)


# -------------------------------------------------
# APPLICATION PERSISTENCE PATHS
# -------------------------------------------------
LOGS_DIRECTORY = "logs"
LOG_FILENAME = "smartorg.log"

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

    report_action = getattr(
        args,
        "action",
        None
    )

    report_reference = getattr(
        args,
        "reference",
        None
    )

    log_info(
        f"{EXECUTION_CONTEXT} | "
        f"task={task} "
        f"path={path} "
        f"report_action={report_action} "
        f"report_reference={report_reference} "
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
            LOGS_DIRECTORY,
            LOG_FILENAME,
            report_action,
            report_reference
        )

    elif task == "rollback":

        handle_rollback(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            dry_run
        )


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()