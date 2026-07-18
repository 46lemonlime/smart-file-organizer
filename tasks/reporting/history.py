# -------------------------------------------------
# REPORT HISTORY
# -------------------------------------------------
"""
Smart File Organizer - Report History

This module builds and resolves unified report history
metadata from persisted execution and rollback reports.

Responsibilities:
- Locate execution and rollback report files
- Build normalized report history entries
- Combine execution and rollback history
- Sort report history deterministically
- Assign stable one-based global indexes
- Resolve history entries by index or identifier
- Preserve history availability when individual reports fail

Architecture Role:
This module owns report history construction and reference
resolution.

It converts persisted report files into lightweight
ReportHistoryItem contracts without rebuilding complete
ExecutionReport or RollbackReport contracts.

History Flow:
execution report files
+
rollback report files
→ normalized history entries
→ deterministic chronological sorting
→ stable global indexing
→ index or identifier resolution

This module intentionally contains NO logic related to:
- complete report contract reconstruction
- report rendering
- report generation
- report saving
- report deletion
- configuration loading
- command-line argument validation
- filesystem mutation

Design Principles:
- deterministic report history
- stable global references
- report-type normalization
- isolated history failures
- dependency on shared persistence helpers
- no complete report deserialization
- structured observability

IMPORTANT:
Filtered history views must preserve the global indexes
assigned by this module.

Filtering must happen after unified history construction and
must never reindex the resulting items.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import ReportHistoryItem

from core.events import (
    REPORT_LOAD_FAILED,
    REPORT_NOT_FOUND
)

from tasks.reporting.storage import (
    build_reports_directory,
    get_report_files,
    get_report_id_from_path,
    read_report_data
)

from utils.logger import (
    log_error,
    log_warning
)


# -------------------------------------------------
# REPORT TYPES
# -------------------------------------------------
REPORT_TYPE_EXECUTION = "execution"
REPORT_TYPE_ROLLBACK = "rollback"


# -------------------------------------------------
# PRIVATE: Build execution history item
# -------------------------------------------------
def _build_execution_history_item(
    report_path: str,
    index: int
) -> ReportHistoryItem:
    """
    Builds report history metadata from an execution report.

    Execution skipped totals combine discovery-stage and
    planning-stage skipped items.

    ARGS:
        report_path:
            Path to the persisted execution report.

        index:
            Temporary or final history index.

    RETURNS:
        ReportHistoryItem
    """

    report_data = read_report_data(
        report_path
    )

    mover_data = report_data.get(
        "mover",
        report_data.get("execution")
    )

    discovery_data = report_data["discovery"]
    planning_data = report_data["planning"]

    total_skipped = (
        discovery_data["total_skipped"]
        + planning_data["total_skipped"]
    )

    return ReportHistoryItem(
        index=index,
        report_id=get_report_id_from_path(
            report_path
        ),
        report_type=REPORT_TYPE_EXECUTION,
        path=report_path,
        dry_run=mover_data["dry_run"],
        total_processed=mover_data["total_processed"],
        total_skipped=total_skipped,
        total_failed=mover_data["total_failed"]
    )


# -------------------------------------------------
# PRIVATE: Build rollback history item
# -------------------------------------------------
def _build_rollback_history_item(
    report_path: str,
    index: int
) -> ReportHistoryItem:
    """
    Builds report history metadata from a rollback report.

    Rollback reports do not currently persist rollback-planning
    skipped operations. Therefore, total_skipped remains zero.

    ARGS:
        report_path:
            Path to the persisted rollback report.

        index:
            Temporary or final history index.

    RETURNS:
        ReportHistoryItem
    """

    report_data = read_report_data(
        report_path
    )

    return ReportHistoryItem(
        index=index,
        report_id=get_report_id_from_path(
            report_path
        ),
        report_type=REPORT_TYPE_ROLLBACK,
        path=report_path,
        dry_run=report_data["dry_run"],
        total_processed=report_data["total_processed"],
        total_skipped=0,
        total_failed=report_data["total_failed"]
    )


# -------------------------------------------------
# PRIVATE: Reindex report history
# -------------------------------------------------
def _reindex_report_history(
    history_items: list[ReportHistoryItem]
) -> list[ReportHistoryItem]:
    """
    Rebuilds history entries with stable one-based indexes.

    Indexes are assigned only after execution and rollback
    reports have been combined and sorted.

    RETURNS:
        list[ReportHistoryItem]
    """

    indexed_items = []

    for index, item in enumerate(
        history_items,
        start=1
    ):

        indexed_items.append(
            ReportHistoryItem(
                index=index,
                report_id=item.report_id,
                report_type=item.report_type,
                path=item.path,
                dry_run=item.dry_run,
                total_processed=item.total_processed,
                total_skipped=item.total_skipped,
                total_failed=item.total_failed
            )
        )

    return indexed_items


# -------------------------------------------------
# PRIVATE: Append execution history
# -------------------------------------------------
def _append_execution_history(
    history_items: list[ReportHistoryItem],
    report_files: list[str]
) -> None:
    """
    Builds and appends execution history entries.

    Invalid execution reports are logged and skipped so that
    one damaged report does not prevent the remaining history
    from being displayed.
    """

    for report_path in report_files:

        try:

            history_items.append(
                _build_execution_history_item(
                    report_path,
                    index=0
                )
            )

        except Exception as error:

            log_error(
                f"{REPORT_LOAD_FAILED} | "
                f"path={report_path} "
                f"reason=execution_history_build_failed",
                error=error
            )


# -------------------------------------------------
# PRIVATE: Append rollback history
# -------------------------------------------------
def _append_rollback_history(
    history_items: list[ReportHistoryItem],
    report_files: list[str]
) -> None:
    """
    Builds and appends rollback history entries.

    Invalid rollback reports are logged and skipped so that
    one damaged report does not prevent the remaining history
    from being displayed.
    """

    for report_path in report_files:

        try:

            history_items.append(
                _build_rollback_history_item(
                    report_path,
                    index=0
                )
            )

        except Exception as error:

            log_error(
                f"{REPORT_LOAD_FAILED} | "
                f"path={report_path} "
                f"reason=rollback_history_build_failed",
                error=error
            )


# -------------------------------------------------
# PRIVATE: Resolve report history item
# -------------------------------------------------
def _resolve_report_history_item(
    reference: str,
    history_items: list[ReportHistoryItem]
) -> ReportHistoryItem | None:
    """
    Resolves a history entry by global index or identifier.

    Numeric references are interpreted as one-based global
    history indexes.

    Non-numeric references are interpreted as report
    identifiers.

    If an identifier matches multiple reports, the reference
    is considered ambiguous and cannot be resolved.

    RETURNS:
        ReportHistoryItem | None
    """

    if reference.isdigit():

        requested_index = int(reference)

        for item in history_items:

            if item.index == requested_index:

                return item

        return None

    matching_items = [
        item
        for item in history_items
        if item.report_id == reference
    ]

    if len(matching_items) == 1:

        return matching_items[0]

    if len(matching_items) > 1:

        log_warning(
            f"{REPORT_NOT_FOUND} | "
            f"reference={reference} "
            f"reason=ambiguous_report_id"
        )

    return None


# -------------------------------------------------
# PUBLIC: List report history
# -------------------------------------------------
def list_report_history(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> list[ReportHistoryItem]:
    """
    Builds unified chronological report history.

    Execution and rollback reports are normalized into a
    shared ReportHistoryItem contract.

    ORDER GUARANTEES:
    - execution and rollback reports are combined
    - report type does not affect sorting
    - reports are sorted by report identifier
    - sorting is descending
    - one-based indexes are assigned after sorting
    - indexes represent positions in unified global history

    RETURNS:
        list[ReportHistoryItem]

    IMPORTANT:
    Consumers may filter the returned list, but must preserve
    the indexes assigned here.
    """

    execution_reports_path = build_reports_directory(
        reports_directory,
        execution_reports_directory
    )

    rollback_reports_path = build_reports_directory(
        reports_directory,
        rollback_reports_directory
    )

    execution_files = get_report_files(
        execution_reports_path
    )

    rollback_files = get_report_files(
        rollback_reports_path
    )

    history_items = []

    _append_execution_history(
        history_items,
        execution_files
    )

    _append_rollback_history(
        history_items,
        rollback_files
    )

    history_items.sort(
        key=lambda item: item.report_id,
        reverse=True
    )

    return _reindex_report_history(
        history_items
    )


# -------------------------------------------------
# PUBLIC: Find report history item
# -------------------------------------------------
def find_report_history_item(
    reference: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> ReportHistoryItem | None:
    """
    Finds report history metadata by global index or report
    identifier.

    Supported references:
        "1"
        "2"
        "20260710T090146"

    This function resolves history metadata only. It does not
    rebuild the complete execution or rollback report.

    RETURNS:
        ReportHistoryItem | None
    """

    history_items = list_report_history(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    history_item = _resolve_report_history_item(
        reference,
        history_items
    )

    if history_item is None:

        log_warning(
            f"{REPORT_NOT_FOUND} | "
            f"reference={reference}"
        )

        return None

    return history_item