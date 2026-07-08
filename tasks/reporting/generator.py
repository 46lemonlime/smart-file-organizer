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

mover report
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
    DiscoverySkippedItem,
    ExecutionPlan,
    ExecutionReport,
    MoverReport,
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
    skipped_items: list[DiscoverySkippedItem]
) -> DiscoveryReport:
    """
    Builds the discovery-stage report contract.

    IMPORTANT:
    Skipped items are supplied by the discovery subsystem
    through the DiscoveryResult contract to preserve
    end-to-end discovery traceability.
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
        total_skipped=len(skipped_items),
        categories=category_reports,
        skipped_items=skipped_items
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
        total_skipped=len(plan.skipped),
        skipped_operations=plan.skipped
    )


# -------------------------------------------------
# PUBLIC: Build execution report
# -------------------------------------------------
def build_execution_report(
    path: str,
    discovery: DiscoveryReport,
    planning: PlanningReport,
    mover: MoverReport
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
        mover=mover
    )