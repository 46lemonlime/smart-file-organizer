# -------------------------------------------------
# REPORT LOADER
# -------------------------------------------------
"""
Smart File Organizer - Report Persistence Loader

This module loads persisted structured application reports
and exposes report history metadata.

Responsibilities:
- Locate saved report files
- Read report JSON files
- Deserialize report data
- Rebuild report contracts
- Build unified report history entries
- Resolve report history items by index or identifier
- Load reports by index or identifier
- Return validated report contracts

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- report generation
- report rendering
- report saving
- report deletion
- configuration loading

Instead, it functions as the reporting persistence loading
layer responsible for reading already-saved report data,
exposing report history metadata, and reconstructing
validated report contracts.

Loading Flow:
JSON file
→ deserialization
→ contract reconstruction
→ validated report contract

History Flow:
execution report files
+
rollback report files
→ normalized history metadata
→ chronological report history
→ index or identifier resolution

Configuration:
Report locations are injected by the application's
composition root.

This module never:
- reads configuration files
- loads AppConfig
- determines report locations
- deletes report files

Design Principles:
- load-only responsibility
- deterministic report history
- no report generation
- no report rendering
- no report saving
- no report deletion
- dependency injection
- contract-first loading boundary
- automatic contract validation
- structured observability

IMPORTANT:
This module reads persisted report data and rebuilds report
contracts using persistence configuration supplied by the
application.

It does NOT:
- generate reports
- render reports
- save reports
- delete reports
- mutate reports
- own configuration
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import json
import os

from core.contracts import (
    CategoryReport,
    DiscoveryReport,
    DiscoverySkippedItem,
    ExecutionReport,
    ExecutionResult,
    MoverReport,
    PlanningReport,
    ReportHistoryItem,
    RollbackReport,
    RollbackResult,
    SkippedOperation
)

from core.events import (
    REPORT_LOAD_START,
    REPORT_LOAD_COMPLETE,
    REPORT_LOAD_FAILED,
    REPORT_NOT_FOUND
)

from utils.logger import log_info, log_warning, log_error


# -------------------------------------------------
# PRIVATE: Build reports directory
# -------------------------------------------------
def _build_reports_directory(
    reports_directory: str,
    report_subdirectory: str
) -> str:
    """
    Builds a report directory path.
    """

    return os.path.join(
        reports_directory,
        report_subdirectory
    )


# -------------------------------------------------
# PRIVATE: Read report data
# -------------------------------------------------
def _read_report_data(
    report_path: str
) -> dict:
    """
    Reads and deserializes persisted report JSON data.

    PURPOSE:
    - centralize JSON report loading
    - avoid duplicated file access logic
    - preserve consistent encoding behavior
    """

    with open(
        report_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# -------------------------------------------------
# PRIVATE: Extract report identifier
# -------------------------------------------------
def _get_report_id_from_path(
    report_path: str
) -> str:
    """
    Extracts a report identifier from its filename.

    Example:
        reports/executions/20260708T205244.json

    Returns:
        20260708T205244
    """

    filename = os.path.basename(
        report_path
    )

    report_id, _ = os.path.splitext(
        filename
    )

    return report_id


# -------------------------------------------------
# PRIVATE: Build category reports
# -------------------------------------------------
def _build_category_reports(
    categories_data: list[dict]
) -> list[CategoryReport]:
    """
    Rebuilds category report contracts from serialized data.
    """

    category_reports = []

    for category_data in categories_data:

        category_reports.append(
            CategoryReport(
                category=category_data["category"],
                files=category_data["files"]
            )
        )

    return category_reports


# -------------------------------------------------
# PRIVATE: Build discovery skipped items
# -------------------------------------------------
def _build_discovery_skipped_items(
    skipped_items_data: list[dict]
) -> list[DiscoverySkippedItem]:
    """
    Rebuilds discovery skipped item contracts from serialized data.
    """

    skipped_items = []

    for skipped_item_data in skipped_items_data:

        skipped_items.append(
            DiscoverySkippedItem(
                name=skipped_item_data["name"],
                source_path=skipped_item_data["source_path"],
                reason=skipped_item_data["reason"]
            )
        )

    return skipped_items


# -------------------------------------------------
# PRIVATE: Build skipped operations
# -------------------------------------------------
def _build_skipped_operations(
    skipped_operations_data: list[dict]
) -> list[SkippedOperation]:
    """
    Rebuilds skipped operation contracts from serialized data.
    """

    skipped_operations = []

    for skipped_operation_data in skipped_operations_data:

        skipped_operations.append(
            SkippedOperation(
                reason=skipped_operation_data["reason"],
                file=skipped_operation_data.get("file"),
                category=skipped_operation_data.get("category"),
                source_path=skipped_operation_data.get("source_path")
            )
        )

    return skipped_operations


# -------------------------------------------------
# PRIVATE: Build execution results
# -------------------------------------------------
def _build_execution_results(
    results_data: list[dict]
) -> list[ExecutionResult]:
    """
    Rebuilds execution result contracts from serialized data.
    """

    execution_results = []

    for result_data in results_data:

        execution_results.append(
            ExecutionResult(
                category=result_data["category"],
                file=result_data["file"],
                source_path=result_data["source_path"],
                destination_path=result_data["destination_path"],
                status=result_data["status"],
                reason=result_data.get("reason")
            )
        )

    return execution_results


# -------------------------------------------------
# PRIVATE: Build rollback results
# -------------------------------------------------
def _build_rollback_results(
    results_data: list[dict]
) -> list[RollbackResult]:
    """
    Rebuilds rollback result contracts from serialized data.
    """

    rollback_results = []

    for result_data in results_data:

        rollback_results.append(
            RollbackResult(
                category=result_data["category"],
                file=result_data["file"],
                source_path=result_data["source_path"],
                destination_path=result_data["destination_path"],
                status=result_data["status"],
                reason=result_data.get("reason")
            )
        )

    return rollback_results


# -------------------------------------------------
# PRIVATE: Build discovery report
# -------------------------------------------------
def _build_discovery_report(
    discovery_data: dict
) -> DiscoveryReport:
    """
    Rebuilds a discovery report contract from serialized data.

    IMPORTANT:
    skipped_items defaults to an empty list for compatibility
    with older persisted reports created before discovery
    skipped-item tracking was introduced.
    """

    skipped_items = _build_discovery_skipped_items(
        discovery_data.get("skipped_items", [])
    )

    return DiscoveryReport(
        path=discovery_data["path"],
        total_discovered=discovery_data["total_discovered"],
        total_skipped=discovery_data["total_skipped"],
        categories=_build_category_reports(
            discovery_data["categories"]
        ),
        skipped_items=skipped_items
    )


# -------------------------------------------------
# PRIVATE: Build planning report
# -------------------------------------------------
def _build_planning_report(
    planning_data: dict
) -> PlanningReport:
    """
    Rebuilds a planning report contract from serialized data.

    IMPORTANT:
    skipped_operations defaults to an empty list for compatibility
    with older persisted reports created before planning skipped
    operation tracking was introduced.
    """

    skipped_operations = _build_skipped_operations(
        planning_data.get("skipped_operations", [])
    )

    return PlanningReport(
        total_operations=planning_data["total_operations"],
        total_folders=planning_data["total_folders"],
        total_skipped=planning_data["total_skipped"],
        skipped_operations=skipped_operations
    )


# -------------------------------------------------
# PRIVATE: Build mover report
# -------------------------------------------------
def _build_mover_report(
    mover_data: dict
) -> MoverReport:
    """
    Rebuilds a mover report contract from serialized data.

    IMPORTANT:
    results defaults to an empty list for compatibility with
    older persisted reports created before operation-level
    execution result tracking was introduced.
    """

    return MoverReport(
        dry_run=mover_data["dry_run"],
        total_processed=mover_data["total_processed"],
        total_failed=mover_data["total_failed"],
        categories=_build_category_reports(
            mover_data["categories"]
        ),
        results=_build_execution_results(
            mover_data.get("results", [])
        )
    )


# -------------------------------------------------
# PRIVATE: Build execution report
# -------------------------------------------------
def _build_execution_report(
    report_data: dict
) -> ExecutionReport:
    """
    Rebuilds a complete execution report contract from serialized data.
    """

    # -------------------------------------------------
    # MOVER DATA COMPATIBILITY
    # -------------------------------------------------
    # New reports use the "mover" key.
    # Older reports may still use the previous "execution" key.
    mover_data = report_data.get(
        "mover",
        report_data.get("execution")
    )

    return ExecutionReport(
        path=report_data["path"],
        discovery=_build_discovery_report(
            report_data["discovery"]
        ),
        planning=_build_planning_report(
            report_data["planning"]
        ),
        mover=_build_mover_report(
            mover_data
        )
    )


# -------------------------------------------------
# PRIVATE: Build rollback report
# -------------------------------------------------
def _build_rollback_report(
    report_data: dict
) -> RollbackReport:
    """
    Rebuilds a rollback report contract from serialized data.
    """

    return RollbackReport(
        dry_run=report_data["dry_run"],
        total_processed=report_data["total_processed"],
        total_failed=report_data["total_failed"],
        results=_build_rollback_results(
            report_data.get("results", [])
        )
    )


# -------------------------------------------------
# PRIVATE: List report files
# -------------------------------------------------
def _get_report_files(
    reports_path: str
) -> list[str]:
    """
    Returns saved report file paths.
    """

    if not os.path.exists(reports_path):

        return []

    report_files = []

    for filename in os.listdir(reports_path):

        if filename.endswith(".json"):

            report_files.append(
                os.path.join(
                    reports_path,
                    filename
                )
            )

    return report_files


# -------------------------------------------------
# PRIVATE: Build execution history item
# -------------------------------------------------
def _build_execution_history_item(
    report_path: str,
    index: int
) -> ReportHistoryItem:
    """
    Builds a report history entry from an execution report file.

    IMPORTANT:
    Execution skipped totals combine discovery-stage and
    planning-stage skips.
    """

    report_data = _read_report_data(
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
        report_id=_get_report_id_from_path(
            report_path
        ),
        report_type="execution",
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
    Builds a report history entry from a rollback report file.

    IMPORTANT:
    RollbackReport does not currently persist rollback-planning
    skipped operations. Therefore total_skipped is currently 0.
    """

    report_data = _read_report_data(
        report_path
    )

    return ReportHistoryItem(
        index=index,
        report_id=_get_report_id_from_path(
            report_path
        ),
        report_type="rollback",
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

    IMPORTANT:
    Indexes are assigned only after chronological sorting.
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
# PUBLIC: List report history
# -------------------------------------------------
def list_report_history(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> list[ReportHistoryItem]:
    """
    Builds a unified chronological history of persisted reports.

    RETURNS:
        list[ReportHistoryItem]

    ORDER GUARANTEES:
    - combines execution and rollback reports
    - ignores report type when sorting
    - sorts exclusively by report_id (descending)
    - assigns one-based indexes after sorting

    IMPORTANT:
    Execution and rollback reports are combined into a single
    history list. Indexes are assigned after sorting.
    """

    execution_reports_path = _build_reports_directory(
        reports_directory,
        execution_reports_directory
    )

    rollback_reports_path = _build_reports_directory(
        reports_directory,
        rollback_reports_directory
    )

    execution_files = _get_report_files(
        execution_reports_path
    )

    rollback_files = _get_report_files(
        rollback_reports_path
    )

    history_items = []

    for report_path in execution_files:

        try:

            history_items.append(
                _build_execution_history_item(
                    report_path,
                    index=0
                )
            )

        except Exception as e:

            log_error(
                f"{REPORT_LOAD_FAILED} | "
                f"path={report_path} "
                f"reason=execution_history_build_failed",
                error=e
            )

    for report_path in rollback_files:

        try:

            history_items.append(
                _build_rollback_history_item(
                    report_path,
                    index=0
                )
            )

        except Exception as e:

            log_error(
                f"{REPORT_LOAD_FAILED} | "
                f"path={report_path} "
                f"reason=rollback_history_build_failed",
                error=e
            )

    history_items.sort(
        key=lambda item: item.report_id,
        reverse=True
    )

    return _reindex_report_history(
        history_items
    )


# -------------------------------------------------
# PRIVATE: Resolve report history item
# -------------------------------------------------
def _resolve_report_history_item(
    reference: str,
    history_items: list[ReportHistoryItem]
) -> ReportHistoryItem | None:
    """
    Resolves a history entry by one-based index or report identifier.

    IMPORTANT:
    If an identifier matches multiple reports, the reference is
    considered ambiguous. The user should select the report by index.
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
# PUBLIC: Find report history item
# -------------------------------------------------
def find_report_history_item(
    reference: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> ReportHistoryItem | None:
    """
    Finds report history metadata by index or report identifier.

    Supported references:
        "1"
        "2"
        "20260710T090146"

    RETURNS:
        ReportHistoryItem | None

    IMPORTANT:
    This function resolves report history metadata only.
    It does NOT read or rebuild the complete report contract.
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


# -------------------------------------------------
# PRIVATE: Load report from history item
# -------------------------------------------------
def _load_report_from_history_item(
    history_item: ReportHistoryItem
) -> ExecutionReport | RollbackReport:
    """
    Loads and rebuilds the report represented by a history item.
    """

    report_data = _read_report_data(
        history_item.path
    )

    if history_item.report_type == "execution":

        return _build_execution_report(
            report_data
        )

    if history_item.report_type == "rollback":

        return _build_rollback_report(
            report_data
        )

    raise ValueError(
        "Unsupported report history type: "
        f"{history_item.report_type}"
    )


# -------------------------------------------------
# PUBLIC: Load report by reference
# -------------------------------------------------
def load_report_by_reference(
    reference: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> ExecutionReport | RollbackReport | None:
    """
    Loads a persisted report by history index or report identifier.

    Supported references:
        "1"
        "2"
        "20260708T205244"

    RETURNS:
        ExecutionReport | RollbackReport | None
    """

    log_info(
        f"{REPORT_LOAD_START} | "
        f"reference={reference}"
    )

    history_item = find_report_history_item(
        reference,
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if history_item is None:

        return None

    try:

        report = _load_report_from_history_item(
            history_item
        )

        log_info(
            f"{REPORT_LOAD_COMPLETE} | "
            f"path={history_item.path} "
            f"reference={reference}"
        )

        return report

    except Exception as e:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"path={history_item.path} "
            f"reference={reference}",
            error=e
        )

        raise


# -------------------------------------------------
# PUBLIC: Load latest execution report
# -------------------------------------------------
def load_latest_execution_report(
    reports_directory: str,
    execution_reports_directory: str
) -> ExecutionReport | None:
    """
    Loads the latest saved execution report.

    RETURNS:
        ExecutionReport | None

    IMPORTANT:
    This function loads persisted report data and rebuilds
    validated report contracts. It does NOT render, save,
    or generate reports.
    """

    execution_reports_path = _build_reports_directory(
        reports_directory,
        execution_reports_directory
    )

    try:

        log_info(REPORT_LOAD_START)

        report_files = _get_report_files(
            execution_reports_path
        )

        if not report_files:

            log_warning(
                f"{REPORT_NOT_FOUND} | "
                f"path={execution_reports_path}"
            )

            return None

        latest_report_path = max(
            report_files,
            key=os.path.getmtime
        )

        report_data = _read_report_data(
            latest_report_path
        )

        execution_report = _build_execution_report(
            report_data
        )

        log_info(
            f"{REPORT_LOAD_COMPLETE} | "
            f"path={latest_report_path}"
        )

        return execution_report

    except Exception as e:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"path={execution_reports_path}",
            error=e
        )

        raise


# -------------------------------------------------
# PUBLIC: Load latest rollback report
# -------------------------------------------------
def load_latest_rollback_report(
    reports_directory: str,
    rollback_reports_directory: str
) -> RollbackReport | None:
    """
    Loads the latest saved rollback report.

    RETURNS:
        RollbackReport | None

    IMPORTANT:
    This function loads persisted rollback report data and
    rebuilds validated RollbackReport contracts. It does NOT
    render, save, or generate reports.
    """

    rollback_reports_path = _build_reports_directory(
        reports_directory,
        rollback_reports_directory
    )

    try:

        log_info(REPORT_LOAD_START)

        report_files = _get_report_files(
            rollback_reports_path
        )

        if not report_files:

            log_warning(
                f"{REPORT_NOT_FOUND} | "
                f"path={rollback_reports_path}"
            )

            return None

        latest_report_path = max(
            report_files,
            key=os.path.getmtime
        )

        report_data = _read_report_data(
            latest_report_path
        )

        rollback_report = _build_rollback_report(
            report_data
        )

        log_info(
            f"{REPORT_LOAD_COMPLETE} | "
            f"path={latest_report_path}"
        )

        return rollback_report

    except Exception as e:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"path={rollback_reports_path}",
            error=e
        )

        raise