# -------------------------------------------------
# SMART FILE ORGANIZER - REPORT HANDLER
# -------------------------------------------------
"""
Coordinates report presentation and history workflows.

Responsibilities:
- Coordinate unified report history loading
- Coordinate scoped report history filtering
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
→ optional history filtering
→ report contract resolution
→ CLI rendering

Design Principles:
- application-level orchestration
- explicit dependency injection
- deterministic workflow coordination
- subsystem ownership preservation
- stable global report references
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
    ReportHistoryItem,
    RollbackReport,
)

from core.events import (
    REPORT_COMPLETE,
    REPORT_SKIPPED,
    REPORT_START,
)

from tasks.reporting.history import (
    list_report_history,
)

from tasks.reporting.loader import (
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
# REPORT HISTORY SCOPES
# -------------------------------------------------
REPORT_HISTORY_SCOPES = {
    "executions": "execution",
    "rollbacks": "rollback",
}


# -------------------------------------------------
# PUBLIC: Report handler
# -------------------------------------------------
def handle_report(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    reference: str | None,
    report_scope: str | None
) -> None:
    """
    Routes report presentation workflows.

    Supported references:
    - no reference:
        render the latest execution report
    - list:
        render unified chronological report history
    - list executions:
        render execution report history
    - list rollbacks:
        render rollback report history
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
        f"reference={reference or 'latest'} "
        f"scope={report_scope}"
    )

    if reference == "list":

        _handle_report_list(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            report_scope
        )

        return

    if report_scope is not None:

        _render_invalid_report_command()

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=unexpected_report_scope "
            f"reference={reference} "
            f"scope={report_scope}"
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
    rollback_reports_directory: str,
    report_scope: str | None
) -> None:
    """
    Loads, optionally filters, and renders report history.

    IMPORTANT:
    Filtered results preserve their original global history
    indices so report references remain stable across views.
    """

    if (
        report_scope is not None
        and report_scope not in REPORT_HISTORY_SCOPES
    ):

        _render_invalid_report_scope()

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=unsupported_report_scope "
            f"action=list "
            f"scope={report_scope}"
        )

        return

    history_items = list_report_history(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if report_scope is not None:

        history_items = _filter_report_history(
            history_items,
            report_scope
        )

    if not history_items:

        _render_empty_report_history(
            report_scope
        )

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=no_persisted_reports "
            f"action=list "
            f"scope={report_scope or 'all'}"
        )

        return

    render_report_history(
        history_items
    )

    log_info(
        f"{REPORT_COMPLETE} | "
        f"action=list "
        f"scope={report_scope or 'all'} "
        f"reports={len(history_items)}"
    )


# -------------------------------------------------
# PRIVATE: Filter report history
# -------------------------------------------------
def _filter_report_history(
    history_items: list[ReportHistoryItem],
    report_scope: str
) -> list[ReportHistoryItem]:
    """
    Filters unified report history using a supported scope.

    Original global history indices are preserved.
    """

    report_type = REPORT_HISTORY_SCOPES[
        report_scope
    ]

    return [
        history_item
        for history_item in history_items
        if history_item.report_type == report_type
    ]


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
def _render_empty_report_history(
    report_scope: str | None
) -> None:
    """
    Renders feedback when no persisted reports are available.
    """

    print()
    print("Reports")
    print("-------")
    print()

    if report_scope is None:

        print("No reports found.")

    else:

        print(
            f"No {report_scope} reports found."
        )

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
# PRIVATE: Render invalid report scope
# -------------------------------------------------
def _render_invalid_report_scope() -> None:
    """
    Renders feedback for an unsupported report history scope.
    """

    print()
    print("Invalid report history scope.")
    print()
    print("Use:")
    print()
    print("    python3 main.py report list")
    print("    python3 main.py report list executions")
    print("    python3 main.py report list rollbacks")
    print()


# -------------------------------------------------
# PRIVATE: Render invalid report command
# -------------------------------------------------
def _render_invalid_report_command() -> None:
    """
    Renders feedback when a report scope is used without list.
    """

    print()
    print("Invalid report command.")
    print("Report scopes can only be used with 'list'.")
    print()
    print("Use:")
    print()
    print("    python3 main.py report")
    print("    python3 main.py report list")
    print("    python3 main.py report list executions")
    print("    python3 main.py report list rollbacks")
    print("    python3 main.py report <index_or_identifier>")
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