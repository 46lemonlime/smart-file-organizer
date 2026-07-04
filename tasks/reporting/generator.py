# -------------------------------------------------
# REPORT GENERATOR
# -------------------------------------------------
"""
Smart File Organizer - Reporting Contract Generator

This module builds structured reporting contracts from
pipeline execution data.

Responsibilities:
- Build category-level report summaries
- Build discovery-stage reports
- Build planning-stage reports
- Assemble complete execution reports

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- report rendering
- report persistence
- JSON export

Instead, it functions as a pure transformation layer
responsible for converting existing pipeline contracts into
structured reporting contracts.

Reporting Overview:
classified category data
→ category reports

classified discovery data
→ discovery report

execution plan
→ planning report

execution summary
→ execution report assembly

Design Principles:
- pure report contract generation
- deterministic output
- no filesystem access
- no rendering logic
- no persistence logic
- contract-first reporting boundary
- reusable reporting structures

IMPORTANT:
This module only builds report contracts.
It does NOT print, save, export, load, or render reports.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    CategoryReport,
    ClassifiedDiscovery,
    DiscoveryReport,
    ExecutionPlan,
    ExecutionReport,
    ExecutionSummaryReport,
    PlanningReport
)


# -------------------------------------------------
# PUBLIC: Build category reports
# -------------------------------------------------
def build_category_reports(
    category_mapping: dict[str, list[str]]
) -> list[CategoryReport]:
    """
    Builds category report contracts from category-mapped data.

    PURPOSE:
    - centralize category aggregation
    - preserve deterministic reporting output
    - expose reusable category-level reporting logic

    IMPORTANT:
    The reserved 'directories' category is excluded because it
    represents discovered folders, not files to organize.
    """

    category_reports = []

    for category, files in category_mapping.items():

        if category == "directories":
            continue

        category_reports.append(
            CategoryReport(
                category=category,
                files=len(files)
            )
        )

    return category_reports


# -------------------------------------------------
# PUBLIC: Build discovery report
# -------------------------------------------------
def build_discovery_report(
    path: str,
    classified_data: ClassifiedDiscovery,
    total_skipped: int = 0
) -> DiscoveryReport:
    """
    Builds the discovery-stage report contract.

    IMPORTANT:
    total_skipped defaults to 0 because the current discovery
    pipeline calculates skipped items internally but does not yet
    expose them as part of its output contract.
    """

    category_reports = build_category_reports(
        classified_data
    )

    total_discovered = sum(
        category_report.files
        for category_report in category_reports
    )

    return DiscoveryReport(
        path=path,
        total_discovered=total_discovered,
        total_skipped=total_skipped,
        categories=category_reports
    )


# -------------------------------------------------
# PUBLIC: Build planning report
# -------------------------------------------------
def build_planning_report(
    plan: ExecutionPlan
) -> PlanningReport:
    """
    Builds the planning-stage report contract from an execution plan.
    """

    return PlanningReport(
        total_operations=len(plan.operations),
        total_folders=len(plan.folders_to_create),
        total_skipped=len(plan.skipped)
    )


# -------------------------------------------------
# PUBLIC: Build execution report
# -------------------------------------------------
def build_execution_report(
    path: str,
    discovery: DiscoveryReport,
    planning: PlanningReport,
    execution: ExecutionSummaryReport
) -> ExecutionReport:
    """
    Builds the complete execution report contract.

    IMPORTANT:
    This function only assembles already-built report contracts.
    It does NOT render, persist, export, or print the report.
    """

    return ExecutionReport(
        path=path,
        discovery=discovery,
        planning=planning,
        execution=execution
    )