# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION ENTRY POINT
# -------------------------------------------------
"""
This module serves as the application entry point and
top-level orchestration layer.

Responsibilities:
- Parse CLI arguments
- Load application configuration
- Validate execution context
- Route supported tasks
- Coordinate high-level application flow

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- reporting implementation

Instead, it functions as the composition root responsible
for wiring together the application's subsystems.

Application Flow:
CLI
→ configuration loading
→ execution context validation
→ task routing
→ subsystem execution

Subsystems:
- discovery:
    Filesystem discovery and classification
- execution:
    Planning and filesystem mutations
- reporting:
    Execution reporting

Design Principles:
- minimal orchestration
- separation of concerns
- contract-first architecture
- deterministic application flow
- centralized dependency composition

Failure Contract:
- validates execution context before routing
- prevents invalid task execution
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
# Import required libraries
import argparse
import os

# Import modules from the project
from tasks.execution.planner import build_execution_plan
from tasks.discovery.coordinator import discover_files
from tasks.execution.executor import move_files
from tasks.reporting.reporter import generate_report

from utils.logger import log_info, log_error
from utils.config_loader import get_config

from core.metadata import (
    APP_BANNER,
    APP_DESCRIPTION,
    SUPPORTED_TASKS
)

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
    PATH_INVALID,
    TASK_UNKNOWN,
    DISCOVERY_FAILED,
    PLAN_READY,
    MOVE_START,
    MOVE_COMPLETE,
    REPORT_START,
    REPORT_COMPLETE
)

# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------
def handle_move(
    path: str,
    dry_run: bool,
    folder_prefix: str
) -> None:
    """
    Executes the full organization pipeline.
    """

    log_info(
        f"{MOVE_START} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    classified_data = discover_files(path)

    # -------------------------------------------------
    # DISCOVERY VALIDATION
    # -------------------------------------------------
    if classified_data is None:

        log_error(
            f"{DISCOVERY_FAILED} | "
            f"reason=discovery_returned_none "
            f"path={path}"
        )

        return

    # -------------------------------------------------
    # STEP 2: BUILD EXECUTION PLAN
    # -------------------------------------------------
    plan = build_execution_plan(
        path,
        classified_data,
        folder_prefix
    )

    # -------------------------------------------------
    # PLAN SUMMARY
    # -------------------------------------------------
    log_info(
        f"{PLAN_READY} | "
        f"operations={len(plan.operations)} "
        f"folders={len(plan.folders_to_create)} "
        f"skipped={len(plan.skipped)}"
    )

    # -------------------------------------------------
    # STEP 3: EXECUTE PLAN
    # -------------------------------------------------
    move_files(
        plan.operations,
        dry_run
    )

    log_info(
        f"{MOVE_COMPLETE} | "
        f"dry_run={dry_run}"
    )


# -------------------------------------------------
# REPORT HANDLER
# -------------------------------------------------
def handle_report(path: str) -> None:
    """
    Executes reporting workflow.
    """

    log_info(
        f"{REPORT_START} | "
        f"path={path}"
    )

    generate_report(path)

    log_info(
        f"{REPORT_COMPLETE} | "
        f"path={path}"
    )


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main() -> None:
    """
    CLI entry point.
    """

    # -------------------------------------------------
    # CLI SETUP
    # -------------------------------------------------
    parser = argparse.ArgumentParser(
        description=APP_DESCRIPTION
    )

    parser.add_argument("task", type=str)
    parser.add_argument("path", type=str)

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate filesystem changes"
    )

    args = parser.parse_args()

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    config = get_config()

    dry_run = args.dry_run or config.dry_run

    folder_prefix = config.folder_prefix

    # -------------------------------------------------
    # STARTUP
    # -------------------------------------------------
    log_info(
        f"{APP_START} | "
        f"banner={APP_BANNER}"
    )

    # -------------------------------------------------
    # PATH VALIDATION
    # -------------------------------------------------
    if not os.path.exists(args.path):

        log_error(
            f"{PATH_INVALID} | "
            f"reason=path_not_found "
            f"path={args.path}"
        )

        return

    # -------------------------------------------------
    # TASK VALIDATION
    # -------------------------------------------------
    task = args.task.lower()

    if task not in SUPPORTED_TASKS:

        log_error(
            f"{TASK_UNKNOWN} | "
            f"reason=unsupported_task "
            f"task={args.task}"
        )

        return

    # -------------------------------------------------
    # EXECUTION CONTEXT
    # -------------------------------------------------
    log_info(
        f"{EXECUTION_CONTEXT} | "
        f"task={task} "
        f"path={args.path} "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # TASK ROUTING
    # -------------------------------------------------
    if task == "move":

        handle_move(
            args.path,
            dry_run,
            folder_prefix
        )

    elif task == "report":

        handle_report(args.path)


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()