# -------------------------------------------------
# SMART FILE ORGANIZER - MOVE HANDLER
# -------------------------------------------------
"""
Coordinates the complete move workflow.

Responsibilities:
- Coordinate filesystem discovery
- Coordinate execution planning
- Coordinate filesystem mutations or dry-run simulation
- Coordinate execution report generation
- Coordinate report persistence
- Coordinate CLI report rendering
- Emit move workflow observability events

Architecture Role:
This module defines the application-level move workflow.

It composes specialized discovery, execution, and reporting
subsystems without implementing their internal behavior.

Workflow:
discovery
→ execution planning
→ filesystem execution or simulation
→ report generation
→ report persistence
→ CLI rendering

Design Principles:
- application-level orchestration
- explicit dependency injection
- deterministic workflow coordination
- subsystem ownership preservation
- minimal business logic

IMPORTANT:
This module coordinates the move workflow only.

It does NOT:
- discover or classify files
- build execution plans
- mutate the filesystem directly
- generate report contracts
- persist reports directly
- render reports directly
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.events import (
    DISCOVERY_FAILED,
    MOVE_COMPLETE,
    MOVE_START,
    PLAN_READY,
)

from core.paths import EXECUTION_REPORTS_DIRECTORY

from tasks.discovery.coordinator import discover_files

from tasks.execution.mover import move_files
from tasks.execution.planner import build_execution_plan

from tasks.reporting.generator import (
    build_discovery_report,
    build_execution_report,
    build_planning_report,
)

from tasks.reporting.reporter import render_execution_report
from tasks.reporting.saver import save_report

from utils.logger import log_error, log_info


# -------------------------------------------------
# PUBLIC: Move handler
# -------------------------------------------------
def handle_move(
    path: str,
    dry_run: bool,
    folder_prefix: str
) -> None:
    """
    Executes the complete file organization workflow.

    Workflow:
    discovery
    → execution planning
    → filesystem execution or simulation
    → report generation
    → report persistence
    → CLI rendering

    IMPORTANT:
    Specialized behavior remains delegated to its owning
    subsystem. This handler only coordinates the workflow.
    """

    log_info(
        f"{MOVE_START} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    discovery_result = discover_files(
        path
    )

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
    # STEP 4: BUILD EXECUTION REPORT
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
    save_report(
        execution_report,
        EXECUTION_REPORTS_DIRECTORY
    )

    # -------------------------------------------------
    # STEP 6: RENDER EXECUTION REPORT
    # -------------------------------------------------
    render_execution_report(
        execution_report
    )

    log_info(
        f"{MOVE_COMPLETE} | "
        f"dry_run={execution_report.mover.dry_run} "
        f"processed={execution_report.mover.total_processed} "
        f"failed={execution_report.mover.total_failed}"
    )