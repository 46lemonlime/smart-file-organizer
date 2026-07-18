# -------------------------------------------------
# REPORT LOADER
# -------------------------------------------------
"""
Smart File Organizer - Report Loader

This module coordinates persisted report loading workflows.

Responsibilities:
- Load reports by history index or identifier
- Load the latest execution report
- Load the latest rollback report
- Coordinate report history resolution
- Coordinate persistence access
- Delegate contract reconstruction
- Return validated report contracts
- Provide structured loading observability

Architecture Role:
This module is the reporting persistence loading coordinator.

It does not directly own:
- JSON file access
- report file discovery
- report identifier extraction
- report history construction
- report history indexing
- report reference resolution
- contract reconstruction
- report generation
- report rendering
- report saving
- report deletion
- configuration loading

Loading Flow:
report reference
→ report history resolution
→ persisted data loading
→ contract deserialization
→ validated report contract

Latest Report Flow:
report directory
→ saved report discovery
→ deterministic latest-file selection
→ persisted data loading
→ contract deserialization
→ validated report contract

Dependencies:
- storage.py owns persistence helpers
- history.py owns report history and reference resolution
- deserializer.py owns contract reconstruction

Configuration:
Report locations are injected by the application's
composition root.

Design Principles:
- workflow coordination only
- deterministic report selection
- dependency delegation
- contract-first loading boundary
- no configuration ownership
- no rendering responsibility
- no persistence mutation
- structured observability

IMPORTANT:
This module reads already-persisted report data through the
shared reporting storage helpers.

It does NOT:
- generate reports
- render reports
- save reports
- delete reports
- mutate reports
- build report history
- deserialize nested contracts directly
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    ExecutionReport,
    ReportHistoryItem,
    RollbackReport
)

from core.events import (
    REPORT_LOAD_COMPLETE,
    REPORT_LOAD_FAILED,
    REPORT_LOAD_START,
    REPORT_NOT_FOUND
)

from tasks.reporting.deserializer import (
    build_execution_report,
    build_rollback_report
)

from tasks.reporting.history import (
    REPORT_TYPE_EXECUTION,
    REPORT_TYPE_ROLLBACK,
    find_report_history_item
)

from tasks.reporting.storage import (
    build_reports_directory,
    get_latest_report_path,
    read_report_data
)

from utils.logger import (
    log_error,
    log_info,
    log_warning
)


# -------------------------------------------------
# PRIVATE: Load report from history item
# -------------------------------------------------
def _load_report_from_history_item(
    history_item: ReportHistoryItem
) -> ExecutionReport | RollbackReport:
    """
    Loads and rebuilds the report represented by a history
    item.

    The history item determines:
    - the persisted report path
    - the report type
    - the deserializer to use

    RETURNS:
        ExecutionReport | RollbackReport

    RAISES:
        ValueError:
            If the history item contains an unsupported report
            type.
    """

    report_data = read_report_data(
        history_item.path
    )

    if history_item.report_type == REPORT_TYPE_EXECUTION:

        return build_execution_report(
            report_data
        )

    if history_item.report_type == REPORT_TYPE_ROLLBACK:

        return build_rollback_report(
            report_data
        )

    raise ValueError(
        "Unsupported report history type: "
        f"{history_item.report_type}"
    )


# -------------------------------------------------
# PRIVATE: Load latest report data
# -------------------------------------------------
def _load_latest_report_data(
    reports_path: str
) -> tuple[str, dict] | None:
    """
    Locates and reads the latest persisted report.

    Latest-report selection is delegated to storage.py so all
    reporting workflows use the same deterministic report
    identifier ordering.

    RETURNS:
        tuple[str, dict] | None

        The tuple contains:
        - latest report path
        - deserialized report data
    """

    latest_report_path = get_latest_report_path(
        reports_path
    )

    if latest_report_path is None:

        log_warning(
            f"{REPORT_NOT_FOUND} | "
            f"path={reports_path}"
        )

        return None

    report_data = read_report_data(
        latest_report_path
    )

    return (
        latest_report_path,
        report_data
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
    Loads a persisted report by global history index or report
    identifier.

    Supported references:
        "1"
        "2"
        "20260708T205244"

    The reference is resolved against unified execution and
    rollback report history.

    RETURNS:
        ExecutionReport | RollbackReport | None

    IMPORTANT:
    Numeric references represent stable global history indexes.

    Identifier references must match exactly one report.
    Ambiguous or unknown references return None.
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
            f"reference={reference} "
            f"report_type={history_item.report_type}"
        )

        return report

    except Exception as error:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"path={history_item.path} "
            f"reference={reference} "
            f"report_type={history_item.report_type}",
            error=error
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

    Latest selection is based on the report identifier encoded
    in the report filename, not on filesystem modification
    time.

    RETURNS:
        ExecutionReport | None

    IMPORTANT:
    This function does not render, save, generate, or mutate
    reports.
    """

    execution_reports_path = build_reports_directory(
        reports_directory,
        execution_reports_directory
    )

    log_info(
        f"{REPORT_LOAD_START} | "
        f"report_type={REPORT_TYPE_EXECUTION} "
        f"path={execution_reports_path}"
    )

    try:

        latest_report = _load_latest_report_data(
            execution_reports_path
        )

        if latest_report is None:

            return None

        latest_report_path, report_data = latest_report

        execution_report = build_execution_report(
            report_data
        )

        log_info(
            f"{REPORT_LOAD_COMPLETE} | "
            f"report_type={REPORT_TYPE_EXECUTION} "
            f"path={latest_report_path}"
        )

        return execution_report

    except Exception as error:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"report_type={REPORT_TYPE_EXECUTION} "
            f"path={execution_reports_path}",
            error=error
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

    Latest selection is based on the report identifier encoded
    in the report filename, not on filesystem modification
    time.

    RETURNS:
        RollbackReport | None

    IMPORTANT:
    This function does not render, save, generate, or mutate
    reports.
    """

    rollback_reports_path = build_reports_directory(
        reports_directory,
        rollback_reports_directory
    )

    log_info(
        f"{REPORT_LOAD_START} | "
        f"report_type={REPORT_TYPE_ROLLBACK} "
        f"path={rollback_reports_path}"
    )

    try:

        latest_report = _load_latest_report_data(
            rollback_reports_path
        )

        if latest_report is None:

            return None

        latest_report_path, report_data = latest_report

        rollback_report = build_rollback_report(
            report_data
        )

        log_info(
            f"{REPORT_LOAD_COMPLETE} | "
            f"report_type={REPORT_TYPE_ROLLBACK} "
            f"path={latest_report_path}"
        )

        return rollback_report

    except Exception as error:

        log_error(
            f"{REPORT_LOAD_FAILED} | "
            f"report_type={REPORT_TYPE_ROLLBACK} "
            f"path={rollback_reports_path}",
            error=error
        )

        raise