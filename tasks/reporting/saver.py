# -------------------------------------------------
# REPORT SAVER
# -------------------------------------------------
"""
Smart File Organizer - Report Persistence Saver

This module persists structured application reports.

Responsibilities:
- Serialize application reports
- Persist reports as JSON files
- Create the destination directory when needed
- Return the saved report path

Architecture Role:
This module is the reporting persistence layer responsible
only for saving already-built report contracts.

Persistence Flow:
report contract
→ JSON serialization
→ filesystem persistence
→ saved report path

The destination directory is supplied by the caller.

This module does NOT:
- read configuration files
- load AppConfig
- determine application persistence locations
- generate reports
- render reports
- load reports
- list reports
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from core.contracts import (
    ExecutionReport,
    RollbackReport,
)

from core.events import (
    REPORT_SAVED,
    REPORT_SAVE_FAILED,
)

from utils.logger import log_error, log_info


# -------------------------------------------------
# PRIVATE: Ensure destination directory
# -------------------------------------------------
def _ensure_destination_directory(
    destination_directory: Path
) -> None:
    """
    Ensures that the report destination directory exists.
    """

    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )


# -------------------------------------------------
# PRIVATE: Build report filename
# -------------------------------------------------
def _build_report_filename() -> str:
    """
    Builds a unique timestamp-based report filename.

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
    destination_directory: Path,
) -> Path:
    """
    Saves a report contract as a JSON file.

    Returns:
        Path: path to the saved report file
    """

    try:

        _ensure_destination_directory(
            destination_directory
        )

        report_path = (
            destination_directory
            / _build_report_filename()
        )

        with report_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                asdict(report),
                file,
                indent=4,
            )

        log_info(
            f"{REPORT_SAVED} | "
            f"path={report_path}"
        )

        return report_path

    except Exception as error:

        log_error(
            f"{REPORT_SAVE_FAILED} | "
            f"destination={destination_directory}",
            error=error,
        )

        raise