# -------------------------------------------------
# REPORT CLEANER
# -------------------------------------------------
"""
Smart File Organizer - Persistence Cleaner

This module deletes persisted application reports
and clears persisted application logs.

Responsibilities:
- Resolve persisted reports by history index or identifier
- Delete individual persisted reports
- Delete reports by report type
- Delete the complete persisted report history
- Clear the application log file
- Validate persisted artifact availability
- Return metadata about deleted reports
- Preserve cleanup observability

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- user file mutations
- rollback execution
- report generation
- report rendering
- report saving
- report reconstruction
- report history construction
- configuration loading
- logging implementation

Instead, it functions as the persistence cleanup layer
responsible only for deleting saved reports and clearing
the application log file.

Individual Report Deletion Flow:
report reference
→ history item resolution
→ report path validation
→ filesystem deletion
→ deleted ReportHistoryItem

Bulk Report Deletion Flow:
deletion scope
→ unified report history
→ scope filtering
→ filesystem deletion
→ list[ReportHistoryItem]

Log Cleanup Flow:
log directory
+
log filename
→ log path validation
→ file truncation
→ cleanup result

Configuration:
Persisted artifact locations are injected by the
application's composition root.

This module never:
- reads configuration files
- loads AppConfig
- constructs report history
- renders CLI output
- mutates report contents
- removes report directories
- deletes organized user files

Design Principles:
- cleanup-only responsibility
- dependency injection
- contract-first cleanup boundary
- deterministic report resolution
- explicit filesystem validation
- per-report failure isolation
- safe log truncation
- structured observability

IMPORTANT:
This module deletes application-generated metadata only.

It does NOT:
- rollback file operations
- reverse executions
- delete organized user files
- generate reports
- render reports
- own configuration
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os

from core.contracts import ReportHistoryItem

from core.events import (
    REPORT_DELETE_START,
    REPORT_DELETED,
    REPORT_DELETE_FAILED,
    REPORT_NOT_FOUND
)

from tasks.reporting.loader import (
    find_report_history_item,
    list_report_history
)

from utils.logger import log_info, log_warning, log_error


# -------------------------------------------------
# PRIVATE: Delete report file
# -------------------------------------------------
def _delete_report_file(
    report_path: str
) -> None:
    """
    Deletes a persisted report file.

    PURPOSE:
    - isolate filesystem deletion
    - keep public workflows readable
    - preserve a clear persistence boundary

    IMPORTANT:
    Report resolution and path validation must occur
    before calling this helper.
    """

    os.remove(
        report_path
    )


# -------------------------------------------------
# PRIVATE: Clear log file
# -------------------------------------------------
def _clear_log_file(
    log_path: str
) -> None:
    """
    Clears a persisted application log file.

    PURPOSE:
    - isolate log truncation
    - preserve the existing log file
    - avoid requiring the logger to recreate the file

    IMPORTANT:
    The log path must be validated before calling this helper.
    """

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ):
        pass


# -------------------------------------------------
# PRIVATE: Filter report history by scope
# -------------------------------------------------
def _filter_report_history_by_scope(
    history_items: list[ReportHistoryItem],
    scope: str
) -> list[ReportHistoryItem]:
    """
    Filters report history entries using a supported deletion scope.

    Supported scopes:
    - executions
    - rollbacks
    - all

    IMPORTANT:
    Report history ordering is preserved.
    """

    if scope == "all":

        return history_items

    report_type_by_scope = {
        "executions": "execution",
        "rollbacks": "rollback"
    }

    report_type = report_type_by_scope.get(
        scope
    )

    if report_type is None:

        raise ValueError(
            f"Unsupported report deletion scope: {scope}"
        )

    return [
        history_item
        for history_item in history_items
        if history_item.report_type == report_type
    ]


# -------------------------------------------------
# PUBLIC: Delete report by reference
# -------------------------------------------------
def delete_report_by_reference(
    reference: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> ReportHistoryItem | None:
    """
    Deletes a persisted report by history index or identifier.

    Supported references:
        "1"
        "2"
        "20260710T090146"

    RETURNS:
        ReportHistoryItem:
            metadata describing the deleted report

        None:
            if the reference cannot be resolved or the persisted
            report file no longer exists

    IMPORTANT:
    This function deletes report metadata only.
    It does NOT reverse or mutate any user file operation.
    """

    report_path = "unknown"

    try:

        log_info(
            f"{REPORT_DELETE_START} | "
            f"reference={reference} "
            f"artifact_type=report"
        )

        # -------------------------------------------------
        # STEP 1: RESOLVE REPORT HISTORY ITEM
        # -------------------------------------------------
        history_item = find_report_history_item(
            reference,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        if history_item is None:

            log_warning(
                f"{REPORT_NOT_FOUND} | "
                f"reference={reference} "
                f"artifact_type=report "
                f"reason=invalid_report_reference"
            )

            return None

        report_path = history_item.path

        # -------------------------------------------------
        # STEP 2: VALIDATE REPORT FILE
        # -------------------------------------------------
        if not os.path.isfile(report_path):

            log_warning(
                f"{REPORT_NOT_FOUND} | "
                f"reference={reference} "
                f"artifact_type=report "
                f"path={report_path} "
                f"reason=report_file_missing"
            )

            return None

        # -------------------------------------------------
        # STEP 3: DELETE REPORT FILE
        # -------------------------------------------------
        _delete_report_file(
            report_path
        )

        log_info(
            f"{REPORT_DELETED} | "
            f"reference={reference} "
            f"artifact_type=report "
            f"report_id={history_item.report_id} "
            f"report_type={history_item.report_type} "
            f"path={report_path}"
        )

        return history_item

    except Exception as e:

        log_error(
            f"{REPORT_DELETE_FAILED} | "
            f"reference={reference} "
            f"artifact_type=report "
            f"path={report_path}",
            error=e
        )

        raise


# -------------------------------------------------
# PUBLIC: Delete reports by scope
# -------------------------------------------------
def delete_reports_by_scope(
    scope: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> list[ReportHistoryItem]:
    """
    Deletes persisted reports using a report history scope.

    Supported scopes:
        executions:
            deletes all persisted execution reports

        rollbacks:
            deletes all persisted rollback reports

        all:
            deletes all persisted execution and rollback reports

    RETURNS:
        list[ReportHistoryItem]:
            metadata describing successfully deleted reports

    IMPORTANT:
    - report directories are preserved
    - failures are isolated per report
    - an empty list indicates that no matching reports were deleted
    - this function never deletes organized user files
    """

    log_info(
        f"{REPORT_DELETE_START} | "
        f"scope={scope} "
        f"artifact_type=report"
    )

    # -------------------------------------------------
    # STEP 1: LOAD UNIFIED REPORT HISTORY
    # -------------------------------------------------
    history_items = list_report_history(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    # -------------------------------------------------
    # STEP 2: FILTER REPORTS BY SCOPE
    # -------------------------------------------------
    scoped_items = _filter_report_history_by_scope(
        history_items,
        scope
    )

    if not scoped_items:

        log_warning(
            f"{REPORT_NOT_FOUND} | "
            f"scope={scope} "
            f"artifact_type=report "
            f"reason=no_matching_reports"
        )

        return []

    deleted_items = []

    # -------------------------------------------------
    # STEP 3: DELETE MATCHING REPORT FILES
    # -------------------------------------------------
    for history_item in scoped_items:

        report_path = history_item.path

        try:

            if not os.path.isfile(report_path):

                log_warning(
                    f"{REPORT_NOT_FOUND} | "
                    f"artifact_type=report "
                    f"report_id={history_item.report_id} "
                    f"report_type={history_item.report_type} "
                    f"path={report_path} "
                    f"reason=report_file_missing"
                )

                continue

            _delete_report_file(
                report_path
            )

            deleted_items.append(
                history_item
            )

            log_info(
                f"{REPORT_DELETED} | "
                f"scope={scope} "
                f"artifact_type=report "
                f"report_id={history_item.report_id} "
                f"report_type={history_item.report_type} "
                f"path={report_path}"
            )

        except Exception as e:

            log_error(
                f"{REPORT_DELETE_FAILED} | "
                f"scope={scope} "
                f"artifact_type=report "
                f"report_id={history_item.report_id} "
                f"report_type={history_item.report_type} "
                f"path={report_path}",
                error=e
            )

    return deleted_items


# -------------------------------------------------
# PUBLIC: Clear application logs
# -------------------------------------------------
def clear_application_logs(
    logs_directory: str,
    log_filename: str
) -> bool:
    """
    Clears the persisted application log file.

    RETURNS:
        True:
            if the log file was successfully cleared

        False:
            if the log file does not exist

    IMPORTANT:
    This function truncates the existing log file instead of
    deleting it. The logger can therefore continue writing to
    the same path without requiring file recreation.
    """

    log_path = os.path.join(
        logs_directory,
        log_filename
    )

    try:

        log_info(
            f"{REPORT_DELETE_START} | "
            f"artifact_type=logs "
            f"path={log_path}"
        )

        # -------------------------------------------------
        # STEP 1: VALIDATE LOG FILE
        # -------------------------------------------------
        if not os.path.isfile(log_path):

            log_warning(
                f"{REPORT_NOT_FOUND} | "
                f"artifact_type=logs "
                f"path={log_path} "
                f"reason=log_file_missing"
            )

            return False

        # -------------------------------------------------
        # STEP 2: CLEAR LOG FILE
        # -------------------------------------------------
        _clear_log_file(
            log_path
        )

        # This event is written after truncation and may become
        # the first new line in the cleared application log.
        log_info(
            f"{REPORT_DELETED} | "
            f"artifact_type=logs "
            f"path={log_path}"
        )

        return True

    except Exception as e:

        log_error(
            f"{REPORT_DELETE_FAILED} | "
            f"artifact_type=logs "
            f"path={log_path}",
            error=e
        )

        raise