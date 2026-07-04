# -------------------------------------------------
# REPORTER
# -------------------------------------------------
"""
Smart File Organizer - Reporting Presentation Layer

This module renders structured execution reports.

Responsibilities:
- Render execution reports for CLI output
- Present report summaries
- Present category-level report details
- Keep report presentation separate from persistence

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- report generation
- report persistence
- JSON export
- report history

Instead, it functions as the reporting presentation layer
responsible for rendering already-built reporting contracts.

Reporting Flow:
ExecutionReport
→ report summary rendering
→ category detail rendering
→ CLI output

Design Principles:
- presentation-only responsibility
- no report generation
- no filesystem access
- no persistence logic
- contract-first rendering boundary
- deterministic report output
- CLI-first presentation

IMPORTANT:
This module consumes report contracts.
It does NOT build, save, export, load, or mutate reports.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    CategoryReport,
    ExecutionReport
)


# -------------------------------------------------
# PRIVATE: Render section title
# -------------------------------------------------
def _render_section_title(title: str) -> None:
    """
    Renders a report section title.

    PURPOSE:
    - centralize section formatting
    - keep report output visually consistent
    - avoid duplicated CLI formatting
    """

    print()
    print(title)
    print("-" * len(title))


# -------------------------------------------------
# PRIVATE: Render category reports
# -------------------------------------------------
def _render_category_reports(
    categories: list[CategoryReport]
) -> None:
    """
    Renders category-level report data.

    PURPOSE:
    - centralize category rendering
    - keep top-level report rendering readable
    - preserve consistent CLI output formatting
    """

    if not categories:

        print("No category data available.")
        return

    for category_report in categories:

        print(
            f"- {category_report.category}: "
            f"{category_report.files}"
        )


# -------------------------------------------------
# PUBLIC: Render execution report
# -------------------------------------------------
def render_execution_report(
    report: ExecutionReport
) -> None:
    """
    Renders a complete execution report through CLI output.

    IMPORTANT:
    This function only presents report data.
    It does NOT generate, persist, export, load, or mutate reports.
    """

    # -------------------------------------------------
    # REPORT HEADER
    # -------------------------------------------------
    print()
    print("Smart File Organizer Report")
    print("===========================")
    print(f"Path: {report.path}")
    print(f"Mode: {'dry-run' if report.execution.dry_run else 'live'}")

    # -------------------------------------------------
    # DISCOVERY SECTION
    # -------------------------------------------------
    _render_section_title("Discovery")

    print(f"Discovered: {report.discovery.total_discovered}")
    print(f"Skipped: {report.discovery.total_skipped}")

    _render_section_title("Discovery Categories")

    _render_category_reports(
        report.discovery.categories
    )

    # -------------------------------------------------
    # PLANNING SECTION
    # -------------------------------------------------
    _render_section_title("Planning")

    print(f"Operations: {report.planning.total_operations}")
    print(f"Folders: {report.planning.total_folders}")
    print(f"Skipped: {report.planning.total_skipped}")

    # -------------------------------------------------
    # EXECUTION SECTION
    # -------------------------------------------------
    _render_section_title("Execution")

    print(f"Processed: {report.execution.total_processed}")
    print(f"Failed: {report.execution.total_failed}")

    _render_section_title("Execution Categories")

    _render_category_reports(
        report.execution.categories
    )

    print()