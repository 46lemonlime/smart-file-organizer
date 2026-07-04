# -------------------------------------------------
# REPORT LOADER
# -------------------------------------------------
"""
Smart File Organizer - Report Persistence Loader

This module loads persisted structured execution reports.

Responsibilities:
- Locate saved execution reports
- Read execution report JSON files
- Deserialize report data
- Rebuild execution report contracts
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
→ validated ExecutionReport

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
    ExecutionReport,
    ExecutionSummaryReport,
    PlanningReport
)

from core.events import (
    REPORT_LOAD_START,
    REPORT_LOAD_COMPLETE,
    REPORT_LOAD_FAILED,
    REPORT_NOT_FOUND
)

from utils.logger import log_info, log_warning, log_error


# -------------------------------------------------
# PRIVATE: Build execution reports directory
# -------------------------------------------------
def _build_execution_reports_directory(
    reports_directory: str,
    execution_reports_directory: str
) -> str:
    """
    Builds the execution reports directory path.
    """

    return os.path.join(
        reports_directory,
        execution_reports_directory
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
# PRIVATE: Build discovery report
# -------------------------------------------------
def _build_discovery_report(
    discovery_data: dict
) -> DiscoveryReport:
    """
    Rebuilds a discovery report contract from serialized data.
    """

    return DiscoveryReport(
        path=discovery_data["path"],
        total_discovered=discovery_data["total_discovered"],
        total_skipped=discovery_data["total_skipped"],
        categories=_build_category_reports(
            discovery_data["categories"]
        )
    )


# -------------------------------------------------
# PRIVATE: Build planning report
# -------------------------------------------------
def _build_planning_report(
    planning_data: dict
) -> PlanningReport:
    """
    Rebuilds a planning report contract from serialized data.
    """

    return PlanningReport(
        total_operations=planning_data["total_operations"],
        total_folders=planning_data["total_folders"],
        total_skipped=planning_data["total_skipped"]
    )


# -------------------------------------------------
# PRIVATE: Build execution summary report
# -------------------------------------------------
def _build_execution_summary_report(
    execution_data: dict
) -> ExecutionSummaryReport:
    """
    Rebuilds an execution summary report contract from serialized data.
    """

    return ExecutionSummaryReport(
        dry_run=execution_data["dry_run"],
        total_processed=execution_data["total_processed"],
        total_failed=execution_data["total_failed"],
        categories=_build_category_reports(
            execution_data["categories"]
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

    return ExecutionReport(
        path=report_data["path"],
        discovery=_build_discovery_report(
            report_data["discovery"]
        ),
        planning=_build_planning_report(
            report_data["planning"]
        ),
        execution=_build_execution_summary_report(
            report_data["execution"]
        )
    )


# -------------------------------------------------
# PRIVATE: List report files
# -------------------------------------------------
def _get_execution_report_files(
    execution_reports_path: str
) -> list[str]:
    """
    Returns saved execution report file paths.
    """

    if not os.path.exists(execution_reports_path):

        return []

    report_files = []

    for filename in os.listdir(execution_reports_path):

        if filename.endswith(".json"):

            report_files.append(
                os.path.join(
                    execution_reports_path,
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
            _build_execution_reports_directory(
                reports_directory,
                execution_reports_directory
            )
        )

        report_files = _get_execution_report_files(
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