# -------------------------------------------------
# REPORTER
# -------------------------------------------------
"""
Smart File Organizer - Reporting Presentation Layer

This module renders structured application reports.

Responsibilities:
- Render execution reports for CLI output
- Render rollback reports for CLI output
- Present report summaries
- Present category-level report details
- Present skipped discovery items
- Present skipped planning operations
- Present operation-level execution results
- Present operation-level rollback results
- Keep report presentation separate from persistence

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- rollback execution
- report generation
- report persistence
- JSON export
- report history

Instead, it functions as the reporting presentation layer
responsible for rendering already-built reporting contracts.

Reporting Flow:
Report contract
→ report summary rendering
→ detail rendering
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
    DiscoverySkippedItem,
    ExecutionReport,
    ExecutionResult,
    RollbackReport,
    RollbackResult,
    SkippedOperation
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
# PRIVATE: Render discovery skipped items
# -------------------------------------------------
def _render_discovery_skipped_items(
    skipped_items: list[DiscoverySkippedItem]
) -> None:
    """
    Renders discovery-stage skipped item data.

    PURPOSE:
    - centralize discovery skip rendering
    - preserve item-level discovery traceability
    - keep report output visually consistent
    """

    if not skipped_items:

        print("No discovery skipped items.")
        return

    for skipped_item in skipped_items:

        print(
            f"- {skipped_item.name} "
            f"({skipped_item.reason})"
        )


# -------------------------------------------------
# PRIVATE: Render planning skipped operations
# -------------------------------------------------
def _render_planning_skipped_operations(
    skipped_operations: list[SkippedOperation]
) -> None:
    """
    Renders planning-stage skipped operation data.

    PURPOSE:
    - centralize planning skip rendering
    - preserve operation-level planning traceability
    - keep report output visually consistent
    """

    if not skipped_operations:

        print("No planning skipped operations.")
        return

    for skipped_operation in skipped_operations:

        label = skipped_operation.file or "unknown"

        print(
            f"- {label} "
            f"({skipped_operation.reason})"
        )


# -------------------------------------------------
# PRIVATE: Render execution results
# -------------------------------------------------
def _render_execution_results(
    results: list[ExecutionResult]
) -> None:
    """
    Renders operation-level execution result data.

    PURPOSE:
    - centralize execution result rendering
    - keep top-level report rendering readable
    - preserve consistent CLI output formatting
    """

    if not results:

        print("No execution results available.")
        return

    for result in results:

        line = (
            f"- [{result.status}] "
            f"{result.file}"
        )

        if result.reason:

            line += f" ({result.reason})"

        print(line)


# -------------------------------------------------
# PRIVATE: Render rollback results
# -------------------------------------------------
def _render_rollback_results(
    results: list[RollbackResult]
) -> None:
    """
    Renders operation-level rollback result data.

    PURPOSE:
    - centralize rollback result rendering
    - keep top-level report rendering readable
    - preserve consistent CLI output formatting
    """

    if not results:

        print("No rollback results available.")
        return

    for result in results:

        line = (
            f"- [{result.status}] "
            f"{result.file}"
        )

        if result.reason:

            line += f" ({result.reason})"

        print(line)


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
    print(f"Mode: {'dry-run' if report.mover.dry_run else 'live'}")

    # -------------------------------------------------
    # DISCOVERY SECTION
    # -------------------------------------------------
    _render_section_title("Discovery Results")

    print(f"Discovered: {report.discovery.total_discovered}")
    print(f"Skipped: {report.discovery.total_skipped}")

    _render_section_title("Discovery Categories")

    _render_category_reports(
        report.discovery.categories
    )

    _render_section_title("Discovery Skipped Items")

    _render_discovery_skipped_items(
        report.discovery.skipped_items
    )

    # -------------------------------------------------
    # PLANNING SECTION
    # -------------------------------------------------
    _render_section_title("Planning Results")

    print(f"Operations: {report.planning.total_operations}")
    print(f"Folders: {report.planning.total_folders}")
    print(f"Skipped: {report.planning.total_skipped}")

    _render_section_title("Planning Skipped Operations")

    _render_planning_skipped_operations(
        report.planning.skipped_operations
    )

    # -------------------------------------------------
    # MOVER SECTION
    # -------------------------------------------------
    _render_section_title("Mover Results")

    print(f"Processed: {report.mover.total_processed}")
    print(f"Failed: {report.mover.total_failed}")

    _render_section_title("Mover Categories")

    _render_category_reports(
        report.mover.categories
    )

    _render_section_title("Mover Execution Results")

    _render_execution_results(
        report.mover.results
    )

    print()


# -------------------------------------------------
# PUBLIC: Render rollback report
# -------------------------------------------------
def render_rollback_report(
    report: RollbackReport
) -> None:
    """
    Renders a complete rollback report through CLI output.

    IMPORTANT:
    This function only presents rollback report data.
    It does NOT generate, persist, export, load, or mutate reports.
    """

    # -------------------------------------------------
    # REPORT HEADER
    # -------------------------------------------------
    print()
    print("Smart File Organizer Rollback Report")
    print("====================================")
    print(f"Mode: {'dry-run' if report.dry_run else 'live'}")

    # -------------------------------------------------
    # ROLLBACK SECTION
    # -------------------------------------------------
    _render_section_title("Rollback Results")

    print(f"Processed: {report.total_processed}")
    print(f"Failed: {report.total_failed}")

    _render_section_title("Rollback Execution Results")

    _render_rollback_results(
        report.results
    )

    print()