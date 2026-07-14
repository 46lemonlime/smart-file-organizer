# -------------------------------------------------
# SMART FILE ORGANIZER - ROLLBACK HANDLER
# -------------------------------------------------
"""
Coordinates the complete rollback workflow.

Responsibilities:
- Load the latest execution report
- Coordinate rollback planning
- Coordinate rollback execution or dry-run simulation
- Coordinate rollback report persistence
- Coordinate CLI rollback report rendering
- Emit rollback workflow observability events

Architecture Role:
This module defines the application-level rollback workflow.

It composes specialized rollback and reporting subsystems
without implementing their internal behavior.

Workflow:
latest execution report loading
→ rollback planning
→ rollback execution or simulation
→ rollback report persistence
→ CLI rendering

Design Principles:
- application-level orchestration
- explicit dependency injection
- deterministic workflow coordination
- subsystem ownership preservation
- minimal business logic

IMPORTANT:
This module coordinates the rollback workflow only.

It does NOT:
- load persisted reports directly
- build rollback plans
- mutate the filesystem directly
- persist reports directly
- render reports directly
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from tasks.reporting.reporter import render_rollback_report
from tasks.reporting.saver import save_report

from tasks.rollback.coordinator import rollback_latest_execution

from utils.logger import log_info

from core.events import ROLLBACK_COMPLETE

# -------------------------------------------------
# PUBLIC: Rollback handler
# -------------------------------------------------
def handle_rollback(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    dry_run: bool
) -> None:
    """
    Executes the complete rollback workflow.

    Workflow:
    latest execution report loading
    → rollback planning
    → rollback execution or simulation
    → rollback report persistence
    → CLI rendering

    IMPORTANT:
    Rollback behavior remains delegated to the rollback
    subsystem. This handler only coordinates the workflow.
    """

    rollback_report = rollback_latest_execution(
        reports_directory,
        execution_reports_directory,
        dry_run
    )

    if rollback_report is None:

        return

    save_report(
        rollback_report,
        reports_directory,
        rollback_reports_directory
    )

    render_rollback_report(
        rollback_report
    )

    log_info(
        f"{ROLLBACK_COMPLETE} | "
        f"dry_run={rollback_report.dry_run} "
        f"processed={rollback_report.total_processed} "
        f"failed={rollback_report.total_failed}"
    )