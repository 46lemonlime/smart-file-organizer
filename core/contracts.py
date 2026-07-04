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
- execution operations
- execution planning structures
- runtime configuration
- reporting structures

IMPORTANT:
These contracts are shared across multiple subsystems:
- discovery
- execution
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
# VALIDATION HELPERS
# -------------------------------------------------
def _validate_non_empty_string(
    value,
    field_name: str
):
    """
    Validates that a contract field contains
    a non-empty string value.

    PURPOSE:
    - centralize string validation
    - enforce deterministic contract guarantees
    - reduce duplicated validation logic
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

    PURPOSE:
    - centralize list validation
    - enforce stable contract structures
    - reduce duplicated validation logic
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

    PURPOSE:
    - centralize dictionary validation
    - enforce stable contract structures
    - reduce duplicated validation logic
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
# CATEGORY CONFIG CONTRACT
# -------------------------------------------------
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

# -------------------------------------------------
# APPLICATION CONFIG CONTRACT
# -------------------------------------------------
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
    # Dynamic config-driven categories.
    # Keys are category names defined in config.yaml.
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
# DISCOVERY ENTITY CONTRACT
# -------------------------------------------------
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
        """
        Enforces deterministic discovery contract validity.

        PURPOSE:
        - prevent malformed discovery entities
        - centralize structural validation
        - strengthen pipeline guarantees
        """

        # -------------------------------------------------
        # STRING VALIDATION
        # -------------------------------------------------
        _validate_non_empty_string(
            self.name,
            "name"
        )

        _validate_non_empty_string(
            self.full_path,
            "full_path"
        )

        # -------------------------------------------------
        # BOOLEAN VALIDATION
        # -------------------------------------------------
        _validate_bool_type(
            self.is_file,
            "is_file"
        )

        _validate_bool_type(
            self.is_directory,
            "is_directory"
        )


# -------------------------------------------------
# DISCOVERY DATASET CONTRACTS
# -------------------------------------------------
# Raw scanner output contract.
#
# IMPORTANT:
# This structure represents the normalized dataset
# returned by scanner.py after filesystem discovery.
RawDiscoveryDataset: TypeAlias = list[DiscoveredItem]


# Classified discovery output contract.
#
# IMPORTANT:
# Categories are intentionally NOT hardcoded here.
#
# The classification system is fully config-driven and
# categories are defined dynamically via config.yaml.
#
# Example:
# {
#     "images": ["photo.jpg"],
#     "documents": ["notes.pdf"],
#     "music": ["song.mp3"]
# }
ClassifiedDiscovery: TypeAlias = dict[str, list[str]]


# -------------------------------------------------
# EXECUTION ENTITY CONTRACT
# -------------------------------------------------
@dataclass
class ExecutionOperation:
    """
    Represents a single executable filesystem operation.

    CONTRACT GUARANTEES:
    - all required fields are non-empty strings
    - operation structure is deterministic
    - executor-safe structure is enforced

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
        """
        Enforces deterministic execution operation validity.

        PURPOSE:
        - prevent malformed execution operations
        - centralize structural validation
        - strengthen execution guarantees
        """

        # -------------------------------------------------
        # REQUIRED STRING VALIDATION
        # -------------------------------------------------
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


# -------------------------------------------------
# EXECUTION SKIP CONTRACT
# -------------------------------------------------
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
        """
        Enforces deterministic skipped operation validity.

        PURPOSE:
        - prevent malformed skip diagnostics
        - centralize structural validation
        - strengthen planner observability guarantees
        """

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
        _validate_non_empty_string(
            self.reason,
            "reason"
        )

        # -------------------------------------------------
        # OPTIONAL FIELD VALIDATION
        # -------------------------------------------------
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


# -------------------------------------------------
# EXECUTION AGGREGATE CONTRACTS
# -------------------------------------------------
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
        """
        Enforces deterministic execution plan validity.

        PURPOSE:
        - centralize execution plan validation
        - prevent malformed execution structures
        - strengthen planner → executor guarantees
        """

        # -------------------------------------------------
        # LIST STRUCTURE VALIDATION
        # -------------------------------------------------
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

        # -------------------------------------------------
        # FOLDER VALIDATION
        # -------------------------------------------------
        for folder in self.folders_to_create:

            _validate_non_empty_string(
                folder,
                "folders_to_create item"
            )

        # -------------------------------------------------
        # OPERATION CONTRACT VALIDATION
        # -------------------------------------------------
        for operation in self.operations:

            if not isinstance(
                operation,
                ExecutionOperation
            ):

                raise TypeError(
                    "operations must contain "
                    "ExecutionOperation objects"
                )

        # -------------------------------------------------
        # SKIPPED CONTRACT VALIDATION
        # -------------------------------------------------
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
# REPORT CATEGORY CONTRACT
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

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
        _validate_non_empty_string(
            self.category,
            "category"
        )

        _validate_non_negative_int(
            self.files,
            "files"
        )
        

# -------------------------------------------------
# DISCOVERY REPORT CONTRACT
# -------------------------------------------------
@dataclass
class DiscoveryReport:
    """
    Represents the discovery stage summary.

    CONTRACT GUARANTEES:
    - path is a non-empty string
    - totals are non-negative integers
    - categories is list[CategoryReport]

    IMPORTANT:
    This contract contains structured reporting data only.
    It contains NO presentation logic.
    """
    path: str
    total_discovered: int
    total_skipped: int
    categories: list[CategoryReport]

    def __post_init__(self):

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
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

        # -------------------------------------------------
        # CATEGORY REPORT VALIDATION
        # -------------------------------------------------
        for category_report in self.categories:

            if not isinstance(
                category_report,
                CategoryReport
            ):
                raise TypeError(
                    "categories must contain "
                    "CategoryReport objects"
                )


# -------------------------------------------------
# PLANNING REPORT CONTRACT
# -------------------------------------------------
@dataclass
class PlanningReport:
    """
    Represents the execution planning summary.

    CONTRACT GUARANTEES:
    - total_operations is a non-negative integer
    - total_folders is a non-negative integer
    - total_skipped is a non-negative integer

    IMPORTANT:
    This contract describes the generated execution plan.
    It does NOT indicate execution success.
    """
    total_operations: int
    total_folders: int
    total_skipped: int

    def __post_init__(self):

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
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


# -------------------------------------------------
# EXECUTION SUMMARY CONTRACT
# -------------------------------------------------
@dataclass
class ExecutionSummaryReport:
    """
    Represents the final execution outcome.

    CONTRACT GUARANTEES:
    - dry_run is boolean
    - total_processed is a non-negative integer
    - total_failed is a non-negative integer
    - categories is list[CategoryReport]

    IMPORTANT:
    Dry-run and real execution share the same report structure.
    This keeps reporting output deterministic across modes.
    """
    dry_run: bool
    total_processed: int
    total_failed: int
    categories: list[CategoryReport]

    def __post_init__(self):

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
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

        # -------------------------------------------------
        # CATEGORY REPORT VALIDATION
        # -------------------------------------------------
        for category_report in self.categories:

            if not isinstance(
                category_report,
                CategoryReport
            ):
                raise TypeError(
                    "categories must contain "
                    "CategoryReport objects"
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
    - execution is ExecutionSummaryReport

    IMPORTANT:
    This contract aggregates pipeline-stage reports.
    It contains NO rendering logic.
    """
    path: str
    discovery: DiscoveryReport
    planning: PlanningReport
    execution: ExecutionSummaryReport

    def __post_init__(self):

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------
        _validate_non_empty_string(
            self.path,
            "path"
        )

        # -------------------------------------------------
        # REPORT CONTRACT VALIDATION
        # -------------------------------------------------
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
            self.execution,
            ExecutionSummaryReport
        ):
            raise TypeError(
                "execution must be ExecutionSummaryReport"
            )