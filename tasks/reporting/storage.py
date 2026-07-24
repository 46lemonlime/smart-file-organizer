# -------------------------------------------------
# REPORT STORAGE
# -------------------------------------------------
"""
Smart File Organizer - Report Storage

This module provides shared read-only persistence helpers for
saved application reports.

Responsibilities:
- Build report directory paths
- Locate persisted JSON report files
- Read and decode report JSON data
- Extract report identifiers from filenames
- Select the latest report deterministically

Architecture Role:
This module is the low-level read-only persistence boundary
for the reporting subsystem.

It exposes filesystem and JSON operations shared by:
- report history construction
- report loading workflows

Storage Flow:
reports directory
→ report file discovery
→ deterministic report selection
→ JSON decoding
→ deserialized report dictionary

This module intentionally contains NO logic related to:
- report contract reconstruction
- report history item construction
- report history indexing
- report reference resolution
- report generation
- report rendering
- report saving
- report deletion
- configuration loading
- workflow logging
- command-line behavior

Design Principles:
- read-only persistence access
- deterministic report discovery
- centralized filesystem behavior
- centralized JSON decoding
- no application workflow coordination
- no contract dependencies
- no configuration ownership
- no persistence mutation

IMPORTANT:
Report filenames are expected to contain chronologically
sortable report identifiers.

The latest report is selected by report identifier rather than
filesystem modification time. This keeps latest-report loading
consistent with unified report history ordering.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import json
import os


# -------------------------------------------------
# PUBLIC: Build reports directory
# -------------------------------------------------
def build_reports_directory(
    reports_directory: str,
    report_subdirectory: str
) -> str:
    """
    Builds the path of a report subdirectory.

    ARGS:
        reports_directory:
            Root directory containing persisted reports.

        report_subdirectory:
            Execution, rollback, or another report
            subdirectory.

    RETURNS:
        str
    """

    return os.path.join(
        reports_directory,
        report_subdirectory
    )


# -------------------------------------------------
# PUBLIC: Read report data
# -------------------------------------------------
def read_report_data(
    report_path: str
) -> dict:
    """
    Reads and decodes persisted report JSON data.

    ARGS:
        report_path:
            Path to the persisted JSON report.

    RETURNS:
        dict

    RAISES:
        OSError:
            If the report file cannot be opened or read.

        json.JSONDecodeError:
            If the report does not contain valid JSON.
    """

    with open(
        report_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# -------------------------------------------------
# PUBLIC: Get report identifier from path
# -------------------------------------------------
def get_report_id_from_path(
    report_path: str
) -> str:
    """
    Extracts a report identifier from its filename.

    Example:
        reports/executions/20260708T205244.json

    Returns:
        20260708T205244

    ARGS:
        report_path:
            Path to a persisted report.

    RETURNS:
        str
    """

    filename = os.path.basename(
        report_path
    )

    report_id, _ = os.path.splitext(
        filename
    )

    return report_id


# -------------------------------------------------
# PUBLIC: Get report files
# -------------------------------------------------
def get_report_files(
    reports_path: str
) -> list[str]:
    """
    Returns persisted JSON report paths from a directory.

    Missing report directories produce an empty list.

    Only regular files with a case-sensitive ".json"
    extension are included.

    ARGS:
        reports_path:
            Directory containing persisted reports.

    RETURNS:
        list[str]

    IMPORTANT:
    This function does not impose chronological ordering.
    Callers must explicitly apply the ordering required by
    their workflow.
    """

    report_files = []

    try:

        with os.scandir(reports_path) as entries:

            for entry in entries:

                if (
                    entry.name.endswith(".json")
                    and entry.is_file()
                ):

                    report_files.append(
                        entry.path
                    )

    except (FileNotFoundError, NotADirectoryError):

        return []

    return report_files


# -------------------------------------------------
# PUBLIC: Get latest report path
# -------------------------------------------------
def get_latest_report_path(
    reports_path: str
) -> str | None:
    """
    Returns the latest persisted report path.

    Latest selection is based on the report identifier
    extracted from the filename.

    This is consistent with report history, which also orders
    reports by identifier.

    ARGS:
        reports_path:
            Directory containing persisted reports.

    RETURNS:
        str | None

        None is returned when the directory does not contain
        report files.

    IMPORTANT:
    Report identifiers must use a format whose lexical order
    matches chronological order, such as:

        20260708T205244
        20260710T090146
    """

    latest_report_path = None
    latest_report_id = None

    try:

        with os.scandir(reports_path) as entries:

            for entry in entries:

                if (
                    not entry.name.endswith(".json")
                    or not entry.is_file()
                ):
                    continue

                report_id = get_report_id_from_path(
                    entry.name
                )

                if (
                    latest_report_id is None
                    or report_id > latest_report_id
                ):

                    latest_report_id = report_id
                    latest_report_path = entry.path

    except (FileNotFoundError, NotADirectoryError):

        return None

    return latest_report_path