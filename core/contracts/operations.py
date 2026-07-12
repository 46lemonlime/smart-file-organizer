# -------------------------------------------------
# SMART FILE ORGANIZER - OPERATION CONTRACTS
# -------------------------------------------------
"""
Shared operation contracts for Smart File Organizer.

PURPOSE:
- Define deterministic filesystem operation structures
- Represent execution planning data
- Represent skipped planning operations
- Represent operation-level execution results

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- executable filesystem operations
- deterministic execution plans
- skipped operations
- execution outcomes

IMPORTANT:
These contracts contain NO:
- execution planning logic
- filesystem mutation logic
- folder creation logic
- file movement logic
- reporting logic

Execution behavior is implemented by the execution subsystem.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass
from typing import Optional

from .validation import (
    validate_list_type,
    validate_non_empty_string,
)


# -------------------------------------------------
# EXECUTION OPERATION CONTRACT
# -------------------------------------------------
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

        validate_non_empty_string(
            self.category,
            "category"
        )

        validate_non_empty_string(
            self.file,
            "file"
        )

        validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )

        validate_non_empty_string(
            self.folder_name,
            "folder_name"
        )


# -------------------------------------------------
# SKIPPED OPERATION CONTRACT
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

        validate_non_empty_string(
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

                validate_non_empty_string(
                    value,
                    field_name
                )


# -------------------------------------------------
# EXECUTION PLAN CONTRACT
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
    This contract describes execution intent only.
    It does NOT indicate execution success.
    """

    folders_to_create: list[str]
    operations: list[ExecutionOperation]
    skipped: list[SkippedOperation]

    def __post_init__(self):

        validate_list_type(
            self.folders_to_create,
            "folders_to_create"
        )

        validate_list_type(
            self.operations,
            "operations"
        )

        validate_list_type(
            self.skipped,
            "skipped"
        )

        for folder in self.folders_to_create:

            validate_non_empty_string(
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
# EXECUTION RESULT CONTRACT
# -------------------------------------------------
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
    the mover stage.

    It is designed for:
    - detailed reporting
    - execution traceability
    - auditability
    - rollback preparation
    """

    category: str
    file: str
    source_path: str
    destination_path: str
    status: str
    reason: Optional[str] = None

    def __post_init__(self):

        validate_non_empty_string(
            self.category,
            "category"
        )

        validate_non_empty_string(
            self.file,
            "file"
        )

        validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        validate_non_empty_string(
            self.destination_path,
            "destination_path"
        )

        validate_non_empty_string(
            self.status,
            "status"
        )

        if self.reason is not None:

            validate_non_empty_string(
                self.reason,
                "reason"
            )