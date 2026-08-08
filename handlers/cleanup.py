# -------------------------------------------------
# SMART FILE ORGANIZER - CLEANUP HANDLER
# -------------------------------------------------
"""
Coordinates persistence cleanup workflows.

Responsibilities:
- Coordinate individual report deletion
- Coordinate scoped report deletion
- Coordinate application log cleanup
- Coordinate full persistence cleanup
- Provide user-facing cleanup feedback
- Emit cleanup workflow observability events

Architecture Role:
This module defines the application-level cleanup workflow.

It composes specialized cleanup and reporting subsystem
functions without implementing persistence mutations or
report rendering behavior.

Workflow:
cleanup command
→ resource selection
→ cleanup subsystem
→ CLI feedback
→ observability logging

Design Principles:
- application-level orchestration
- centralized application paths
- deterministic workflow coordination
- subsystem ownership preservation
- minimal business logic

IMPORTANT:
This module coordinates cleanup workflows only.

It does NOT:
- delete reports directly
- clear logs directly
- resolve report history internally
- render report contracts
- determine persistence locations
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from pathlib import Path

from core.events import (
    CLEANUP_COMPLETE,
    CLEANUP_SKIPPED,
    CLEANUP_START,
)

from tasks.cleanup.cleaner import (
    clear_application_logs,
    delete_report_by_reference,
    delete_reports_by_scope,
)

from tasks.reporting.reporter import (
    render_deleted_report,
    render_deleted_reports,
)

from utils.logger import log_error, log_info


# -------------------------------------------------
# CLEANUP SCOPES
# -------------------------------------------------
REPORT_DELETION_SCOPES = {
    "executions",
    "rollbacks",
    "all",
}


# -------------------------------------------------
# PUBLIC: Cleanup handler
# -------------------------------------------------
def handle_cleanup(
    log_file_path: Path,
    cleanup_resource: str,
    cleanup_target: str | None,
) -> None:
    """
    Routes persistence cleanup workflows.

    Supported resources:
    - report:
        delete a report by reference or delete reports by scope
    - log:
        clear the application log
    - all:
        delete all reports and clear the application log

    IMPORTANT:
    Persistence mutations remain owned by tasks/cleanup/.
    """

    log_info(
        f"{CLEANUP_START} | "
        f"resource={cleanup_resource} "
        f"target={cleanup_target}"
    )

    if cleanup_resource == "report":

        _handle_report_cleanup(
            cleanup_target
        )

        return

    if cleanup_resource == "log":

        _handle_log_cleanup(
            log_file_path
        )

        return

    if cleanup_resource == "all":

        _handle_full_cleanup(
            log_file_path
        )

        return

    log_error(
        f"{CLEANUP_SKIPPED} | "
        f"reason=unsupported_cleanup_resource "
        f"resource={cleanup_resource}"
    )


# -------------------------------------------------
# PRIVATE: Handle report cleanup
# -------------------------------------------------
def _handle_report_cleanup(
    target: str | None,
) -> None:
    """
    Routes individual and scoped report cleanup workflows.
    """

    if target is None:

        log_error(
            f"{CLEANUP_SKIPPED} | "
            f"reason=missing_report_cleanup_target"
        )

        return

    if target in REPORT_DELETION_SCOPES:

        _handle_scoped_report_cleanup(
            target
        )

        return

    _handle_single_report_cleanup(
        target
    )


# -------------------------------------------------
# PRIVATE: Handle application log cleanup
# -------------------------------------------------
def _handle_log_cleanup(
    log_file_path: Path,
) -> None:
    """
    Clears the persisted application log file.
    """

    logs_cleared = clear_application_logs(
        log_file_path
    )

    if not logs_cleared:

        _render_missing_application_logs()

        log_info(
            f"{CLEANUP_SKIPPED} | "
            f"reason=log_file_not_found "
            f"resource=log"
        )

        return

    _render_cleared_application_logs(
        log_file_path
    )

    log_info(
        f"{CLEANUP_COMPLETE} | "
        f"resource=log"
    )

# -------------------------------------------------
# PRIVATE: Handle full persistence cleanup
# -------------------------------------------------
def _handle_full_cleanup(
    log_file_path: Path,
) -> None:
    """
    Deletes all persisted reports and clears application logs.
    """

    deleted_items = delete_reports_by_scope(
        "all"
    )

    logs_cleared = clear_application_logs(
        log_file_path
    )

    if deleted_items:

        render_deleted_reports(
            deleted_items,
            "all",
        )

    if logs_cleared:

        _render_cleared_application_logs(
            log_file_path
        )

    if not deleted_items and not logs_cleared:

        _render_empty_full_cleanup()

        log_info(
            f"{CLEANUP_SKIPPED} | "
            f"reason=no_persistence_artifacts "
            f"resource=all"
        )

        return

    log_info(
        f"{CLEANUP_COMPLETE} | "
        f"resource=all "
        f"reports_deleted={len(deleted_items)} "
        f"logs_cleared={logs_cleared}"
    )


# -------------------------------------------------
# PRIVATE: Handle scoped report cleanup
# -------------------------------------------------
def _handle_scoped_report_cleanup(
    scope: str,
) -> None:
    """
    Deletes persisted reports matching a supported scope.
    """

    deleted_items = delete_reports_by_scope(
        scope
    )

    if not deleted_items:

        _render_empty_report_cleanup(
            scope
        )

        log_info(
            f"{CLEANUP_SKIPPED} | "
            f"reason=no_matching_reports "
            f"resource=report "
            f"scope={scope}"
        )

        return

    render_deleted_reports(
        deleted_items,
        scope,
    )

    log_info(
        f"{CLEANUP_COMPLETE} | "
        f"resource=report "
        f"scope={scope} "
        f"deleted={len(deleted_items)}"
    )


# -------------------------------------------------
# PRIVATE: Handle individual report cleanup
# -------------------------------------------------
def _handle_single_report_cleanup(
    reference: str,
) -> None:
    """
    Deletes one persisted report by index or identifier.
    """

    deleted_item = delete_report_by_reference(
        reference
    )

    if deleted_item is None:

        _render_invalid_report_reference()

        log_info(
            f"{CLEANUP_SKIPPED} | "
            f"reason=report_delete_not_found "
            f"resource=report "
            f"reference={reference}"
        )

        return

    render_deleted_report(
        deleted_item
    )

    log_info(
        f"{CLEANUP_COMPLETE} | "
        f"resource=report "
        f"report_id={deleted_item.report_id} "
        f"report_type={deleted_item.report_type}"
    )


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
# PRIVATE: Render missing application logs
# -------------------------------------------------
def _render_missing_application_logs() -> None:
    """
    Renders feedback when no application log file exists.
    """

    print()
    print("Logs not found.")
    print("No persisted application log file is available.")
    print()


# -------------------------------------------------
# PRIVATE: Render cleared application logs
# -------------------------------------------------
def _render_cleared_application_logs(
    log_file_path: Path,
) -> None:
    """
    Renders application log cleanup confirmation.
    """

    print()
    print("Cleared Logs")
    print("------------")
    print()
    print(
        f"File: {log_file_path}"
    )
    print()


# -------------------------------------------------
# PRIVATE: Render empty report cleanup
# -------------------------------------------------
def _render_empty_report_cleanup(
    scope: str,
) -> None:
    """
    Renders feedback when no reports match a cleanup scope.
    """

    print()
    print("No reports deleted.")
    print(
        f"No persisted reports matched "
        f"the '{scope}' scope."
    )
    print()


# -------------------------------------------------
# PRIVATE: Render empty full cleanup
# -------------------------------------------------
def _render_empty_full_cleanup() -> None:
    """
    Renders feedback when no persistence artifacts exist.
    """

    print()
    print("Nothing to clean.")
    print("No persisted reports or application logs were found.")
    print()