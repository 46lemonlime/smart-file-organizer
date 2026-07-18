# -------------------------------------------------
# REPORT DESERIALIZER
# -------------------------------------------------
"""
Smart File Organizer - Report Contract Deserializer

This module rebuilds validated report contracts from
deserialized persistence data.

Responsibilities:
- Rebuild nested execution report contracts
- Rebuild rollback report contracts
- Rebuild category report contracts
- Rebuild discovery skipped-item contracts
- Rebuild planning skipped-operation contracts
- Rebuild execution result contracts
- Rebuild rollback result contracts
- Preserve compatibility with older persisted reports
- Return validated report contracts

Architecture Role:
This module functions as the translation boundary between
persisted report data and the application's report contracts.

Deserialization Flow:
deserialized report dictionary
→ nested contract reconstruction
→ automatic contract validation
→ validated report contract

This module intentionally contains NO logic related to:
- filesystem access
- report file discovery
- path construction
- JSON decoding
- report history
- report reference resolution
- report selection
- report generation
- report rendering
- report saving
- report deletion
- configuration loading
- application logging

Design Principles:
- contract-first deserialization
- explicit field mapping
- automatic contract validation
- backward-compatible persistence loading
- no filesystem dependencies
- no configuration ownership
- no workflow coordination

IMPORTANT:
This module expects already-deserialized report dictionaries.

It does NOT:
- open report files
- decode JSON
- locate reports
- select reports
- mutate persisted data
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
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
    Rebuilds discovery skipped-item contracts from serialized data.
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
    Rebuilds skipped-operation contracts from serialized data.
    """

    skipped_operations = []

    for skipped_operation_data in skipped_operations_data:

        skipped_operations.append(
            SkippedOperation(
                reason=skipped_operation_data["reason"],
                file=skipped_operation_data.get("file"),
                category=skipped_operation_data.get("category"),
                source_path=skipped_operation_data.get(
                    "source_path"
                )
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
    Rebuilds execution-result contracts from serialized data.
    """

    execution_results = []

    for result_data in results_data:

        execution_results.append(
            ExecutionResult(
                category=result_data["category"],
                file=result_data["file"],
                source_path=result_data["source_path"],
                destination_path=result_data[
                    "destination_path"
                ],
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
    Rebuilds rollback-result contracts from serialized data.
    """

    rollback_results = []

    for result_data in results_data:

        rollback_results.append(
            RollbackResult(
                category=result_data["category"],
                file=result_data["file"],
                source_path=result_data["source_path"],
                destination_path=result_data[
                    "destination_path"
                ],
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
        discovery_data.get(
            "skipped_items",
            []
        )
    )

    return DiscoveryReport(
        path=discovery_data["path"],
        total_discovered=discovery_data[
            "total_discovered"
        ],
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
    skipped_operations defaults to an empty list for
    compatibility with older persisted reports created before
    planning skipped-operation tracking was introduced.
    """

    skipped_operations = _build_skipped_operations(
        planning_data.get(
            "skipped_operations",
            []
        )
    )

    return PlanningReport(
        total_operations=planning_data[
            "total_operations"
        ],
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
    execution-result tracking was introduced.
    """

    return MoverReport(
        dry_run=mover_data["dry_run"],
        total_processed=mover_data["total_processed"],
        total_failed=mover_data["total_failed"],
        categories=_build_category_reports(
            mover_data["categories"]
        ),
        results=_build_execution_results(
            mover_data.get(
                "results",
                []
            )
        )
    )


# -------------------------------------------------
# PUBLIC: Build execution report
# -------------------------------------------------
def build_execution_report(
    report_data: dict
) -> ExecutionReport:
    """
    Rebuilds a complete execution report contract from
    deserialized persistence data.

    COMPATIBILITY:
    Current reports persist mover data under the "mover" key.
    Older reports may use the previous "execution" key.

    RETURNS:
        ExecutionReport
    """

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
# PUBLIC: Build rollback report
# -------------------------------------------------
def build_rollback_report(
    report_data: dict
) -> RollbackReport:
    """
    Rebuilds a complete rollback report contract from
    deserialized persistence data.

    COMPATIBILITY:
    results defaults to an empty list for older persisted
    reports created before operation-level rollback result
    tracking was introduced.

    RETURNS:
        RollbackReport
    """

    return RollbackReport(
        dry_run=report_data["dry_run"],
        total_processed=report_data["total_processed"],
        total_failed=report_data["total_failed"],
        results=_build_rollback_results(
            report_data.get(
                "results",
                []
            )
        )
    )