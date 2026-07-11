# -------------------------------------------------
# SMART FILE ORGANIZER - CORE CONTRACTS
# -------------------------------------------------
"""
This module defines the core shared contracts used across
the Smart File Organizer pipeline.

PURPOSE:
- Centralize shared pipeline structures
- Define stable inter-module contracts
- Improve architectural consistency
- Reduce dynamic dictionary usage
- Enable stronger type safety

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- discovery entities
- discovery results
- execution operations
- execution planning structures
- execution results
- rollback structures
- runtime configuration
- reporting structures

IMPORTANT:
These contracts are shared across multiple subsystems:
- discovery
- execution
- rollback
- reporting

DESIGN PRINCIPLES:
- deterministic structures
- explicit contracts
- strong typing
- reusable pipeline entities
- centralized schema ownership

NOTE:
Contracts should remain:
- lightweight
- stable
- serialization-friendly
- free of business logic
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass
from typing import Optional, TypeAlias


# -------------------------------------------------
# 1. VALIDATION HELPERS
# -------------------------------------------------
def _validate_non_empty_string(
    value,
    field_name: str
):
    """
    Validates that a contract field contains
    a non-empty string value.
    """

    if not isinstance(value, str):

        raise TypeError(
            f"{field_name} must be str "
            f"(received {type(value).__name__})"
        )

    if not value.strip():

        raise ValueError(
            f"{field_name} cannot be empty"
        )


def _validate_list_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a list.
    """

    if not isinstance(value, list):

        raise TypeError(
            f"{field_name} must be list "
            f"(received {type(value).__name__})"
        )


def _validate_dict_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a dictionary.
    """

    if not isinstance(value, dict):

        raise TypeError(
            f"{field_name} must be dict "
            f"(received {type(value).__name__})"
        )


def _validate_bool_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a boolean.
    """

    if not isinstance(value, bool):

        raise TypeError(
            f"{field_name} must be bool "
            f"(received {type(value).__name__})"
        )


def _validate_non_negative_int(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a non-negative integer.
    """

    if not isinstance(value, int):

        raise TypeError(
            f"{field_name} must be int "
            f"(received {type(value).__name__})"
        )

    if value < 0:

        raise ValueError(
            f"{field_name} cannot be negative"
        )


# -------------------------------------------------
# 2. CONFIGURATION CONTRACTS
# -------------------------------------------------
# CATEGORY CONFIG CONTRACT
@dataclass
class CategoryConfig:
    """
    Represents a configurable file classification category.

    CONTRACT GUARANTEES:
    - description is a non-empty string
    - extensions is a list[str]
    """

    description: str
    extensions: list[str]

    def __post_init__(self):

        _validate_non_empty_string(
            self.description,
            "description"
        )

        _validate_list_type(
            self.extensions,
            "extensions"
        )

        for extension in self.extensions:

            _validate_non_empty_string(
                extension,
                "extensions item"
            )


# APPLICATION CONFIG CONTRACT
@dataclass
class AppConfig:
    """
    Represents the validated runtime configuration.

    CONTRACT GUARANTEES:
    - all required configuration values exist
    - downstream modules never require defaults
    - configuration is fully validated
    """

    folder_prefix: str
    dry_run: bool
    ignore_hidden_files: bool
    ignore_symlinks: bool
    reports_directory: str
    execution_reports_directory: str
    rollback_reports_directory: str
    categories: dict[str, CategoryConfig]

    def __post_init__(self):

        _validate_non_empty_string(
            self.folder_prefix,
            "folder_prefix"
        )

        _validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        _validate_bool_type(
            self.ignore_hidden_files,
            "ignore_hidden_files"
        )

        _validate_bool_type(
            self.ignore_symlinks,
            "ignore_symlinks"
        )

        _validate_dict_type(
            self.categories,
            "categories"
        )

        _validate_non_empty_string(
            self.reports_directory,
            "reports_directory"
        )

        _validate_non_empty_string(
            self.execution_reports_directory,
            "execution_reports_directory"
        )

        _validate_non_empty_string(
            self.rollback_reports_directory,
            "rollback_reports_directory"
        )

        for category_name, category_config in self.categories.items():

            _validate_non_empty_string(
                category_name,
                "category name"
            )

            if not isinstance(
                category_config,
                CategoryConfig
            ):

                raise TypeError(
                    "categories must contain "
                    "CategoryConfig objects"
                )


# -------------------------------------------------
# 3. DISCOVERY CONTRACTS
# -------------------------------------------------
# DISCOVERED ITEM CONTRACT
@dataclass
class DiscoveredItem:
    """
    Represents a raw filesystem entity discovered during scanning.

    CONTRACT GUARANTEES:
    - name is a non-empty string
    - full_path is a non-empty string
    - is_file is boolean
    - is_directory is boolean

    IMPORTANT:
    This contract intentionally contains NO business logic.
    Only structural validation is enforced here.
    """

    name: str
    full_path: str
    is_file: bool
    is_directory: bool

    def __post_init__(self):

        _validate_non_empty_string(
            self.name,
            "name"
        )

        _validate_non_empty_string(
            self.full_path,
            "full_path"
        )

        _validate_bool_type(
            self.is_file,
            "is_file"
        )

        _validate_bool_type(
            self.is_directory,
            "is_directory"
        )


# RAW DISCOVERY DATASET CONTRACT
RawDiscoveryDataset: TypeAlias = list[DiscoveredItem]


# CLASSIFIED DISCOVERY DATASET CONTRACT
ClassifiedDiscovery: TypeAlias = dict[str, list[str]]


# DISCOVERY SKIPPED ITEM CONTRACT
@dataclass
class DiscoverySkippedItem:
    """
    Represents an item skipped during the discovery stage.

    CONTRACT GUARANTEES:
    - name is a non-empty string
    - source_path is a non-empty string
    - reason is a non-empty string

    IMPORTANT:
    This contract preserves item-level discovery skip
    traceability for reporting and future audit workflows.
    """

    name: str
    source_path: str
    reason: str

    def __post_init__(self):

        _validate_non_empty_string(
            self.name,
            "name"
        )

        _validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        _validate_non_empty_string(
            self.reason,
            "reason"
        )


# DISCOVERY RESULT CONTRACT
@dataclass
class DiscoveryResult:
    """
    Represents the complete discovery-stage result.

    CONTRACT GUARANTEES:
    - classified_data is ClassifiedDiscovery
    - skipped_items is list[DiscoverySkippedItem]

    IMPORTANT:
    This contract preserves discovery metadata that does not
    belong inside ClassifiedDiscovery itself.
    """

    classified_data: ClassifiedDiscovery
    skipped_items: list[DiscoverySkippedItem]

    def __post_init__(self):

        _validate_dict_type(
            self.classified_data,
            "classified_data"
        )

        for category, files in self.classified_data.items():

            _validate_non_empty_string(
                category,
                "classified_data category"
            )

            _validate_list_type(
                files,
                "classified_data files"
            )

            for file in files:

                _validate_non_empty_string(
                    file,
                    "classified_data file"
                )

        _validate_list_type(
            self.skipped_items,
            "skipped_items"
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
# 4. EXECUTION PLANNING CONTRACTS
# -------------------------------------------------
# EXECUTION OPERATION CONTRACT
@dataclass
class ExecutionOperation:
    """
    Represents a single executable filesystem operation.

    CONTRACT GUARANTEES:
    - all required fields are non-empty strings
    - operation structure is deterministic
    - mover-safe structure is enforced

    IMPORTANT:
    This contract intentionally contains NO filesystem logic.
    Only structural validation is enforced here.
    """

    category: str
    file: str
    source_path: str
    destination_path: str
    folder_name: str

    def __post_init__(self):

        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_empty_string(
            self.file,
            "file"
        )

        _validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        _validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )

        _validate_non_empty_string(
            self.folder_name,
            "folder_name"
        )


# SKIPPED OPERATION CONTRACT
@dataclass
class SkippedOperation:
    """
    Represents a skipped planning operation.

    CONTRACT GUARANTEES:
    - reason is a non-empty string
    - optional fields must be valid strings if provided
    - deterministic skip structure is enforced

    IMPORTANT:
    This contract intentionally contains NO business logic.
    Only structural validation is enforced here.
    """

    reason: str
    file: Optional[str] = None
    category: Optional[str] = None
    source_path: Optional[str] = None

    def __post_init__(self):

        _validate_non_empty_string(
            self.reason,
            "reason"
        )

        optional_fields = {
            "file": self.file,
            "category": self.category,
            "source_path": self.source_path
        }

        for field_name, value in optional_fields.items():

            if value is not None:

                _validate_non_empty_string(
                    value,
                    field_name
                )


# EXECUTION AGGREGATED PLAN CONTRACT
@dataclass
class ExecutionPlan:
    """
    Represents the deterministic execution plan generated
    before filesystem mutations occur.

    CONTRACT GUARANTEES:
    - folders_to_create is list[str]
    - operations is list[ExecutionOperation]
    - skipped is list[SkippedOperation]

    IMPORTANT:
    This contract intentionally contains NO business logic.
    Only structural validation is enforced here.
    """

    folders_to_create: list[str]
    operations: list[ExecutionOperation]
    skipped: list[SkippedOperation]

    def __post_init__(self):

        _validate_list_type(
            self.folders_to_create,
            "folders_to_create"
        )

        _validate_list_type(
            self.operations,
            "operations"
        )

        _validate_list_type(
            self.skipped,
            "skipped"
        )

        for folder in self.folders_to_create:

            _validate_non_empty_string(
                folder,
                "folders_to_create item"
            )

        for operation in self.operations:

            if not isinstance(
                operation,
                ExecutionOperation
            ):

                raise TypeError(
                    "operations must contain "
                    "ExecutionOperation objects"
                )

        for skipped_operation in self.skipped:

            if not isinstance(
                skipped_operation,
                SkippedOperation
            ):

                raise TypeError(
                    "skipped must contain "
                    "SkippedOperation objects"
                )


# -------------------------------------------------
# 5. EXECUTION RESULT CONTRACTS
# -------------------------------------------------
# EXECUTION RESULT CONTRACT
@dataclass
class ExecutionResult:
    """
    Represents the result of a filesystem execution operation.

    CONTRACT GUARANTEES:
    - category is a non-empty string
    - file is a non-empty string
    - source_path is a non-empty string
    - destination_path is a non-empty string
    - status is a non-empty string
    - reason is optional but must be valid if provided

    IMPORTANT:
    This contract describes what actually happened during
    the mover stage. It is designed for detailed reporting,
    auditability, and future rollback preparation.
    """

    category: str
    file: str
    source_path: str
    destination_path: str
    status: str
    reason: Optional[str] = None

    def __post_init__(self):

        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_empty_string(
            self.file,
            "file"
        )

        _validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        _validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )

        _validate_non_empty_string(
            self.status,
            "status"
        )

        if self.reason is not None:

            _validate_non_empty_string(
                self.reason,
                "reason"
            )


# -------------------------------------------------
# 6. ROLLBACK CONTRACTS
# -------------------------------------------------
# ROLLBACK OPERATION CONTRACT
@dataclass
class RollbackOperation:
    """
    Represents a single rollback filesystem operation.

    CONTRACT GUARANTEES:
    - category is a non-empty string
    - file is a non-empty string
    - source_path is a non-empty string
    - destination_path is a non-empty string

    IMPORTANT:
    A rollback operation reverses a successful mover result:
    - source_path is the current file location
    - destination_path is the original file location
    """

    category: str
    file: str
    source_path: str
    destination_path: str

    def __post_init__(self):

        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_empty_string(
            self.file,
            "file"
        )

        _validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        _validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )


# ROLLBACK PLAN CONTRACT
@dataclass
class RollbackPlan:
    """
    Represents a deterministic rollback plan generated from
    a persisted execution report.

    CONTRACT GUARANTEES:
    - operations is list[RollbackOperation]
    - skipped is list[SkippedOperation]

    IMPORTANT:
    This contract describes rollback intent only.
    It does NOT indicate rollback execution success.
    """

    operations: list[RollbackOperation]
    skipped: list[SkippedOperation]

    def __post_init__(self):

        _validate_list_type(
            self.operations,
            "operations"
        )

        _validate_list_type(
            self.skipped,
            "skipped"
        )

        for operation in self.operations:

            if not isinstance(
                operation,
                RollbackOperation
            ):

                raise TypeError(
                    "operations must contain "
                    "RollbackOperation objects"
                )

        for skipped_operation in self.skipped:

            if not isinstance(
                skipped_operation,
                SkippedOperation
            ):

                raise TypeError(
                    "skipped must contain "
                    "SkippedOperation objects"
                )


# ROLLBACK RESULT CONTRACT
@dataclass
class RollbackResult:
    """
    Represents the result of a rollback filesystem operation.

    CONTRACT GUARANTEES:
    - category is a non-empty string
    - file is a non-empty string
    - source_path is a non-empty string
    - destination_path is a non-empty string
    - status is a non-empty string
    - reason is optional but must be valid if provided
    """

    category: str
    file: str
    source_path: str
    destination_path: str
    status: str
    reason: Optional[str] = None

    def __post_init__(self):

        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_empty_string(
            self.file,
            "file"
        )

        _validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        _validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )

        _validate_non_empty_string(
            self.status,
            "status"
        )

        if self.reason is not None:

            _validate_non_empty_string(
                self.reason,
                "reason"
            )


# ROLLBACK REPORT CONTRACT
@dataclass
class RollbackReport:
    """
    Represents the rollback stage report.

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

        _validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        _validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        _validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )

        _validate_list_type(
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
# 7. REPORTING CONTRACTS
# -------------------------------------------------
# CATEGORY REPORT CONTRACT
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

        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_negative_int(
            self.files,
            "files"
        )


# DISCOVERY REPORT CONTRACT
@dataclass
class DiscoveryReport:
    """
    Represents the discovery stage report.

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

        _validate_non_empty_string(
            self.path,
            "path"
        )

        _validate_non_negative_int(
            self.total_discovered,
            "total_discovered"
        )

        _validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        _validate_list_type(
            self.categories,
            "categories"
        )

        _validate_list_type(
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


# PLANNING REPORT CONTRACT
@dataclass
class PlanningReport:
    """
    Represents the execution planning report.

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

        _validate_non_negative_int(
            self.total_operations,
            "total_operations"
        )

        _validate_non_negative_int(
            self.total_folders,
            "total_folders"
        )

        _validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        _validate_list_type(
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


# MOVER REPORT CONTRACT
@dataclass
class MoverReport:
    """
    Represents the mover stage report.

    CONTRACT GUARANTEES:
    - dry_run is boolean
    - total_processed is a non-negative integer
    - total_failed is a non-negative integer
    - categories is list[CategoryReport]
    - results is list[ExecutionResult]

    IMPORTANT:
    Dry-run and real execution share the same report structure.
    This contract describes the mover stage outcome only.
    It does NOT aggregate the full execution pipeline.
    """

    dry_run: bool
    total_processed: int
    total_failed: int
    categories: list[CategoryReport]
    results: list[ExecutionResult]

    def __post_init__(self):

        _validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        _validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        _validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )

        _validate_list_type(
            self.categories,
            "categories"
        )

        _validate_list_type(
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


# REPORT HISTORY ITEM CONTRACT
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
    This contract contains report history metadata only.
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

        _validate_non_negative_int(
            self.index,
            "index"
        )

        _validate_non_empty_string(
            self.report_id,
            "report_id"
        )

        _validate_non_empty_string(
            self.report_type,
            "report_type"
        )

        _validate_non_empty_string(
            self.path,
            "path"
        )

        _validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        _validate_non_negative_int(
            self.total_processed,
            "total_processed"
        )

        _validate_non_negative_int(
            self.total_skipped,
            "total_skipped"
        )

        _validate_non_negative_int(
            self.total_failed,
            "total_failed"
        )


# EXECUTION REPORT CONTRACT
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

        _validate_non_empty_string(
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