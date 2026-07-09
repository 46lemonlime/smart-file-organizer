# -------------------------------------------------
# REPORT LOADER
# -------------------------------------------------
"""
Smart File Organizer - Report Persistence Loader

This module loads persisted structured application reports.

Responsibilities:
- Locate saved report files
- Read report JSON files
- Deserialize report data
- Rebuild report contracts
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
- report history analysis
- configuration loading

Instead, it functions as the reporting persistence layer
responsible only for loading already-saved report data.

Loading Flow:
JSON file
→ deserialization
→ contract reconstruction
→ validated report contract

Configuration:
The report location is injected by the application's
composition root.

This module never:
- reads configuration files
- loads AppConfig
- determines report locations

Design Principles:
- load-only responsibility
- no report generation
- no report rendering
- no report saving
- dependency injection
- contract-first loading boundary
- automatic contract validation
- structured observability

IMPORTANT:
This module reads persisted report data and rebuilds report
contracts using persistence configuration supplied by the
application.

It does NOT:
- build reports
- render reports
- save reports
- list reports
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
    generate, or list reports.
    """

    try:

        log_info(REPORT_LOAD_START)

        # -------------------------------------------------
        # BUILD REPORT DIRECTORY
        # -------------------------------------------------
        # The report location is injected by the application
        # composition root to keep persistence independent
        # from configuration loading.
        execution_reports_path = (
            _build_reports_directory(
                reports_directory,
                execution_reports_directory
            )
        )

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

        with open(
            latest_report_path,
            "r",
            encoding="utf-8"
        ) as file:

            report_data = json.load(file)

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
    render, save, generate, or list reports.
    """

    try:

        log_info(REPORT_LOAD_START)

        # -------------------------------------------------
        # BUILD REPORT DIRECTORY
        # -------------------------------------------------
        # The report location is injected by the application
        # composition root to keep persistence independent
        # from configuration loading.
        rollback_reports_path = (
            _build_reports_directory(
                reports_directory,
                rollback_reports_directory
            )
        )

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

        with open(
            latest_report_path,
            "r",
            encoding="utf-8"
        ) as file:

            report_data = json.load(file)

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