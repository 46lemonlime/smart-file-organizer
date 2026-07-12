# -------------------------------------------------
# SMART FILE ORGANIZER - RECORD CONTRACTS
# -------------------------------------------------
"""
Shared record contracts for Smart File Organizer.

PURPOSE:
- Define structured reporting data
- Represent execution and rollback reports
- Represent report history metadata
- Provide stable persistence-friendly report contracts

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- category report data
- discovery report data
- planning report data
- mover report data
- execution reports
- rollback reports
- report history entries

IMPORTANT:
These contracts contain NO:
- report generation logic
- report rendering logic
- report loading logic
- report saving logic
- report cleanup logic
- filesystem mutation logic

Reporting behavior is implemented by the reporting subsystem.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass

from .inventory import DiscoverySkippedItem
from .operations import (
    ExecutionResult,
    SkippedOperation,
)
from .recovery import RollbackResult
from .validation import (
    validate_bool_type,
    validate_list_type,
    validate_non_empty_string,
    validate_non_negative_int,
)


# -------------------------------------------------
# CATEGORY REPORT CONTRACT
# -------------------------------------------------
@dataclass
class CategoryReport:
    """
    Represents aggregated report data for a single category.

    CONTRACT GUARANTEES:
    - category is a non-empty string
    - files is a non-negative integer

    IMPORTANT:
    This contract contains reporting data only.
    It contains NO classification logic.
    """

    category: str
    files: int

    def __post_init__(self):

        validate_non_empty_string(
            self.category,
            "category"
        )

        validate_non_negative_int(
            self.files,
            "files"
        )


# -------------------------------------------------
# DISCOVERY REPORT CONTRACT
# -------------------------------------------------
@dataclass
class DiscoveryReport:
    """
    Represents the discovery-stage report.

    CONTRACT GUARANTEES:
    - path is a non-empty string
    - totals are non-negative integers
    - categories is list[CategoryReport]
    - skipped_items is list[DiscoverySkippedItem]

    IMPORTANT:
    This contract contains structured reporting data only.
    It contains NO presentation logic.
    """

    path: str
    total_discovered: int
    total_skipped: int
    categories: list[CategoryReport]
    skipped_items: list[DiscoverySkippedItem]

    def __post_init__(self):

        validate_non_empty_string(
            self.path,
            "path"
        )

        validate_non_negative_int(
            self.total_discovered,
            "total_discovered"
        )

        validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        validate_list_type(
            self.categories,
            "categories"
        )

        validate_list_type(
            self.skipped_items,
            "skipped_items"
        )

        for category_report in self.categories:

            if not isinstance(
                category_report,
                CategoryReport
            ):

                raise TypeError(
                    "categories must contain "
                    "CategoryReport objects"
                )

        for skipped_item in self.skipped_items:

            if not isinstance(
                skipped_item,
                DiscoverySkippedItem
            ):

                raise TypeError(
                    "skipped_items must contain "
                    "DiscoverySkippedItem objects"
                )


# -------------------------------------------------
# PLANNING REPORT CONTRACT
# -------------------------------------------------
@dataclass
class PlanningReport:
    """
    Represents the execution-planning report.

    CONTRACT GUARANTEES:
    - total_operations is a non-negative integer
    - total_folders is a non-negative integer
    - total_skipped is a non-negative integer
    - skipped_operations is list[SkippedOperation]

    IMPORTANT:
    This contract describes the generated execution plan.
    It does NOT indicate execution success.
    """

    total_operations: int
    total_folders: int
    total_skipped: int
    skipped_operations: list[SkippedOperation]

    def __post_init__(self):

        validate_non_negative_int(
            self.total_operations,
            "total_operations"
        )

        validate_non_negative_int(
            self.total_folders,
            "total_folders"
        )

        validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        validate_list_type(
            self.skipped_operations,
            "skipped_operations"
        )

        for skipped_operation in self.skipped_operations:

            if not isinstance(
                skipped_operation,
                SkippedOperation
            ):

                raise TypeError(
                    "skipped_operations must contain "
                    "SkippedOperation objects"
                )


# -------------------------------------------------
# MOVER REPORT CONTRACT
# -------------------------------------------------
@dataclass
class MoverReport:
    """
    Represents the mover-stage report.

    CONTRACT GUARANTEES:
    - dry_run is boolean
    - total_processed is a non-negative integer
    - total_failed is a non-negative integer
    - categories is list[CategoryReport]
    - results is list[ExecutionResult]

    IMPORTANT:
    Dry-run and real execution share the same report structure.

    This contract describes the mover-stage outcome only.
    It does NOT aggregate the complete execution pipeline.
    """

    dry_run: bool
    total_processed: int
    total_failed: int
    categories: list[CategoryReport]
    results: list[ExecutionResult]

    def __post_init__(self):

        validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )

        validate_list_type(
            self.categories,
            "categories"
        )

        validate_list_type(
            self.results,
            "results"
        )

        for category_report in self.categories:

            if not isinstance(
                category_report,
                CategoryReport
            ):

                raise TypeError(
                    "categories must contain "
                    "CategoryReport objects"
                )

        for execution_result in self.results:

            if not isinstance(
                execution_result,
                ExecutionResult
            ):

                raise TypeError(
                    "results must contain "
                    "ExecutionResult objects"
                )


# -------------------------------------------------
# EXECUTION REPORT CONTRACT
# -------------------------------------------------
@dataclass
class ExecutionReport:
    """
    Represents the complete structured report for one execution.

    CONTRACT GUARANTEES:
    - path is a non-empty string
    - discovery is DiscoveryReport
    - planning is PlanningReport
    - mover is MoverReport

    IMPORTANT:
    This contract aggregates pipeline-stage reports.
    It contains NO rendering logic.
    """

    path: str
    discovery: DiscoveryReport
    planning: PlanningReport
    mover: MoverReport

    def __post_init__(self):

        validate_non_empty_string(
            self.path,
            "path"
        )

        if not isinstance(
            self.discovery,
            DiscoveryReport
        ):

            raise TypeError(
                "discovery must be DiscoveryReport"
            )

        if not isinstance(
            self.planning,
            PlanningReport
        ):

            raise TypeError(
                "planning must be PlanningReport"
            )

        if not isinstance(
            self.mover,
            MoverReport
        ):

            raise TypeError(
                "mover must be MoverReport"
            )


# -------------------------------------------------
# ROLLBACK REPORT CONTRACT
# -------------------------------------------------
@dataclass
class RollbackReport:
    """
    Represents the rollback-stage report.

    CONTRACT GUARANTEES:
    - dry_run is boolean
    - total_processed is a non-negative integer
    - total_failed is a non-negative integer
    - results is list[RollbackResult]

    IMPORTANT:
    Dry-run and real rollback share the same report structure.
    """

    dry_run: bool
    total_processed: int
    total_failed: int
    results: list[RollbackResult]

    def __post_init__(self):

        validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )

        validate_list_type(
            self.results,
            "results"
        )

        for result in self.results:

            if not isinstance(
                result,
                RollbackResult
            ):

                raise TypeError(
                    "results must contain "
                    "RollbackResult objects"
                )


# -------------------------------------------------
# REPORT HISTORY ITEM CONTRACT
# -------------------------------------------------
@dataclass
class ReportHistoryItem:
    """
    Represents a summarized persisted report entry.

    CONTRACT GUARANTEES:
    - index is a non-negative integer
    - report_id is a non-empty string
    - report_type is a non-empty string
    - path is a non-empty string
    - dry_run is boolean
    - totals are non-negative integers

    IMPORTANT:
    This contract contains report-history metadata only.
    It is designed for report listing and report selection.
    """

    index: int
    report_id: str
    report_type: str
    path: str
    dry_run: bool
    total_processed: int
    total_skipped: int
    total_failed: int

    def __post_init__(self):

        validate_non_negative_int(
            self.index,
            "index"
        )

        validate_non_empty_string(
            self.report_id,
            "report_id"
        )

        validate_non_empty_string(
            self.report_type,
            "report_type"
        )

        validate_non_empty_string(
            self.path,
            "path"
        )

        validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )