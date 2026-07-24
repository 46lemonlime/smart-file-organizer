# -------------------------------------------------
# REPORT SAVER
# -------------------------------------------------
"""
Smart File Organizer - Report Persistence Saver

This module persists structured application reports.

Responsibilities:
- Serialize application reports
- Persist reports as JSON files
- Create report output directories
- Return the saved report path

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- report generation
- report rendering
- report loading
- report history querying
- configuration loading

Instead, it functions as the reporting persistence layer
responsible only for saving already-built report contracts.

Persistence Flow:
report contract
→ JSON serialization
→ filesystem persistence
→ saved report path

Configuration:
The persistence location is injected by the application's
composition root.

This module never:
- reads configuration files
- loads AppConfig
- determines persistence locations

Design Principles:
- save-only responsibility
- contract-first persistence boundary
- dependency injection
- deterministic JSON serialization
- structured observability

IMPORTANT:
This module consumes report contracts and persistence
configuration supplied by the application.

It does NOT:
- build reports
- render reports
- load reports
- list reports
- mutate reports
- own configuration
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import json
import os
from dataclasses import asdict
from datetime import datetime

from core.contracts import (
    ExecutionReport,
    RollbackReport
)

from utils.logger import log_info, log_error

from core.events import (
    REPORT_SAVED,
    REPORT_SAVE_FAILED
)


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
# PRIVATE: Ensure reports directory
# -------------------------------------------------
def _ensure_reports_directory(
    reports_path: str
) -> None:
    """
    Ensures that a report directory exists.
    """

    os.makedirs(
        reports_path,
        exist_ok=True
    )


# -------------------------------------------------
# PRIVATE: Build report filename
# -------------------------------------------------
def _build_report_filename() -> str:
    """
    Builds a unique timestamp-based report filename.

    IMPORTANT:
    Colons are intentionally removed to keep filenames portable
    across operating systems.
    """

    timestamp = datetime.now().isoformat(
        timespec="microseconds"
    )

    safe_timestamp = (
        timestamp
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
    )

    return f"{safe_timestamp}.json"


# -------------------------------------------------
# PUBLIC: Save report
# -------------------------------------------------
def save_report(
    report: ExecutionReport | RollbackReport,
    reports_directory: str,
    report_subdirectory: str
) -> str:
    """
    Saves a report contract as a JSON file.

    RETURNS:
        str: path to the saved report file

    IMPORTANT:
    This function only persists an already-built report contract.
    It does NOT generate, render, load, or list reports.
    """

    try:

        # -------------------------------------------------
        # BUILD REPORT DIRECTORY
        # -------------------------------------------------
        # The report output location is injected by the
        # application composition root to keep persistence
        # independent from configuration loading.
        reports_path = (
            _build_reports_directory(
                reports_directory,
                report_subdirectory
            )
        )

        _ensure_reports_directory(
            reports_path
        )

        filename = _build_report_filename()

        report_path = os.path.join(
            reports_path,
            filename
        )

        with open(report_path, "w", encoding="utf-8") as file:

            json.dump(
                asdict(report),
                file,
                indent=4
            )

        log_info(
            f"{REPORT_SAVED} | "
            f"path={report_path}"
        )

        return report_path

    except Exception as e:

        log_error(
            f"{REPORT_SAVE_FAILED} | "
            f"path={getattr(report, 'path', 'unknown')}",
            error=e
        )

        raise