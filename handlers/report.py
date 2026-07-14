# -------------------------------------------------
# SMART FILE ORGANIZER - REPORT HANDLER
# -------------------------------------------------
"""
Coordinates report presentation and history workflows.

Responsibilities:
- Coordinate unified report history loading
- Coordinate latest execution report loading
- Coordinate report selection by index or identifier
- Select the appropriate report renderer
- Provide user-facing report feedback
- Emit report workflow observability events

Architecture Role:
This module defines the application-level report workflow.

It composes specialized reporting subsystem functions without
implementing report loading, reconstruction, or rendering.

Workflow:
report command
→ report loading or history construction
→ report contract resolution
→ CLI rendering

Design Principles:
- application-level orchestration
- explicit dependency injection
- deterministic workflow coordination
- subsystem ownership preservation
- minimal business logic

IMPORTANT:
This module coordinates report presentation workflows only.

It does NOT:
- generate reports
- save reports
- deserialize report data
- construct report history
- resolve persisted files directly
- delete reports
- clear application logs
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    ExecutionReport,
    RollbackReport,
)

from core.events import (
    REPORT_COMPLETE,
    REPORT_SKIPPED,
    REPORT_START,
)

from tasks.reporting.loader import (
    list_report_history,
    load_latest_execution_report,
    load_report_by_reference,
)

from tasks.reporting.reporter import (
    render_execution_report,
    render_report_history,
    render_rollback_report,
)

from utils.logger import log_error, log_info


# -------------------------------------------------
# PUBLIC: Report handler
# -------------------------------------------------
def handle_report(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    reference: str | None
) -> None:
    """
    Routes report presentation workflows.

    Supported references:
    - no reference:
        render the latest execution report
    - list:
        render unified chronological report history
    - numeric index:
        render a report selected from history
    - report identifier:
        render a report selected by identifier

    IMPORTANT:
    Report cleanup is coordinated independently by
    the cleanup handler.
    """

    log_info(
        f"{REPORT_START} | "
        f"reference={reference or 'latest'}"
    )

    if reference == "list":

        _handle_report_list(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        return

    _handle_report_show(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory,
        reference
    )


# -------------------------------------------------
# PRIVATE: Handle report list
# -------------------------------------------------
def _handle_report_list(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> None:
    """
    Loads and renders unified chronological report history.
    """

    history_items = list_report_history(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if not history_items:

        _render_empty_report_history()

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=no_persisted_reports "
            f"action=list"
        )

        return

    render_report_history(
        history_items
    )

    log_info(
        f"{REPORT_COMPLETE} | "
        f"action=list "
        f"reports={len(history_items)}"
    )


# -------------------------------------------------
# PRIVATE: Handle report presentation
# -------------------------------------------------
def _handle_report_show(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    reference: str | None
) -> None:
    """
    Loads and renders the latest or selected persisted report.
    """

    if reference is None:

        report = load_latest_execution_report(
            reports_directory,
            execution_reports_directory
        )

        report_reference = "latest"

    else:

        report = load_report_by_reference(
            reference,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        report_reference = reference

    if report is None:

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=report_not_found "
            f"reference={report_reference}"
        )

        if reference is None:

            _render_missing_latest_execution_report()

        else:

            _render_invalid_report_reference()

        return

    report_type = _render_report_contract(
        report
    )

    if report_type is None:

        return

    log_info(
        f"{REPORT_COMPLETE} | "
        f"type={report_type} "
        f"reference={report_reference}"
    )


# -------------------------------------------------
# PRIVATE: Render report contract
# -------------------------------------------------
def _render_report_contract(
    report: ExecutionReport | RollbackReport
) -> str | None:
    """
    Selects the renderer for a supported report contract.

    RETURNS:
        str:
            rendered report type

        None:
            if the contract type is unsupported
    """

    if isinstance(
        report,
        ExecutionReport
    ):

        render_execution_report(
            report
        )

        return "execution"

    if isinstance(
        report,
        RollbackReport
    ):

        render_rollback_report(
            report
        )

        return "rollback"

    log_error(
        f"{REPORT_SKIPPED} | "
        f"reason=unsupported_report_contract "
        f"type={type(report).__name__}"
    )

    return None


# -------------------------------------------------
# PRIVATE: Render empty report history
# -------------------------------------------------
def _render_empty_report_history() -> None:
    """
    Renders feedback when no persisted reports are available.
    """

    print()
    print("Reports")
    print("-------")
    print()
    print("No reports found.")
    print()


# -------------------------------------------------
# PRIVATE: Render invalid report reference
# -------------------------------------------------
def _render_invalid_report_reference() -> None:
    """
    Renders feedback for an invalid report index or identifier.
    """

    print()
    print("Report not found.")
    print("Invalid report index or identifier.")
    print()
    print("Use:")
    print()
    print("    python3 main.py report list")
    print()
    print("to view available reports.")
    print()


# -------------------------------------------------
# PRIVATE: Render missing latest execution report
# -------------------------------------------------
def _render_missing_latest_execution_report() -> None:
    """
    Renders feedback when no execution report is available.
    """

    print()
    print("Report not found.")
    print("No persisted execution reports are available.")
    print()