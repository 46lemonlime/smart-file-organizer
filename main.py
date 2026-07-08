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

Architecture Role:
This file intentionally contains NO logic related to:
- CLI parser construction
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- reporting implementation

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
- reporting:
    Execution reporting

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
import os

# Import modules from the project
from tasks.execution.planner import build_execution_plan
from tasks.discovery.coordinator import discover_files
from tasks.execution.mover import move_files
from tasks.reporting.loader import load_latest_execution_report
from tasks.reporting.reporter import render_execution_report

from cli.parser import parse_args

from tasks.reporting.generator import (
    build_discovery_report,
    build_planning_report,
    build_execution_report
)

from tasks.reporting.saver import save_execution_report

from utils.logger import log_info, log_error
from utils.config_loader import get_config

from core.metadata import (
    APP_BANNER
)

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
    REPORT_SKIPPED,
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
    folder_prefix: str,
    reports_directory: str,
    execution_reports_directory: str
) -> None:
    """
    Executes the full organization pipeline.

    IMPORTANT:
    Reporting persistence configuration is injected by
    the application composition root.

    This handler coordinates report generation while
    delegating persistence to the reporting subsystem.
    """

    log_info(
        f"{MOVE_START} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    discovery_result = discover_files(path)

    # -------------------------------------------------
    # DISCOVERY VALIDATION
    # -------------------------------------------------
    if discovery_result is None:

        log_error(
            f"{DISCOVERY_FAILED} | "
            f"reason=discovery_returned_none "
            f"path={path}"
        )

        return

    classified_data = discovery_result.classified_data

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
    mover_report = move_files(
        plan.operations,
        dry_run
    )

    # -------------------------------------------------
    # STEP 4: GENERATE EXECUTION REPORT
    # -------------------------------------------------
    discovery_report = build_discovery_report(
        path,
        classified_data,
        skipped_items=discovery_result.skipped_items
    )

    planning_report = build_planning_report(
        plan
    )

    execution_report = build_execution_report(
        path,
        discovery_report,
        planning_report,
        mover_report
    )

    # -------------------------------------------------
    # STEP 5: SAVE EXECUTION REPORT
    # -------------------------------------------------
    # Reports are generated automatically for every move
    # execution, but they are not rendered automatically.
    save_execution_report(
        execution_report,
        reports_directory,
        execution_reports_directory
    )

    log_info(
        f"{MOVE_COMPLETE} | "
        f"dry_run={execution_report.mover.dry_run} "
        f"processed={execution_report.mover.total_processed} "
        f"failed={execution_report.mover.total_failed}"
    )


# -------------------------------------------------
# REPORT HANDLER
# -------------------------------------------------
def handle_report(
    reports_directory: str,
    execution_reports_directory: str
) -> None:
    """
    Executes reporting presentation workflow.

    IMPORTANT:
    Reports are loaded from persisted execution report files.
    This handler does NOT generate new reports.
    """

    log_info(REPORT_START)

    # -------------------------------------------------
    # STEP 1: LOAD LATEST REPORT
    # -------------------------------------------------
    report = load_latest_execution_report(
        reports_directory,
        execution_reports_directory
    )

    # -------------------------------------------------
    # REPORT AVAILABILITY VALIDATION
    # -------------------------------------------------
    if report is None:

        log_info(
            f"{REPORT_SKIPPED} | "
            "reason=no_persisted_reports"
        )

        return

    # -------------------------------------------------
    # STEP 2: RENDER LOADED REPORT
    # -------------------------------------------------
    render_execution_report(
        report
    )

    log_info(
        f"{REPORT_COMPLETE} | "
        f"path={report.path}"
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

    dry_run = getattr(args, "dry_run", False) or config.dry_run

    folder_prefix = config.folder_prefix

    reports_directory = config.reports_directory

    execution_reports_directory = (
        config.execution_reports_directory
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

    path = getattr(args, "path", None)

    log_info(
        f"{EXECUTION_CONTEXT} | "
        f"task={task} "
        f"path={path} "
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
            execution_reports_directory
        )


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()