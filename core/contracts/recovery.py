# -------------------------------------------------
# SMART FILE ORGANIZER - RECOVERY CONTRACTS
# -------------------------------------------------
"""
Shared recovery contracts for Smart File Organizer.

PURPOSE:
- Define rollback operation structures
- Represent rollback planning data
- Represent operation-level rollback results

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- rollback operations
- rollback plans
- rollback results

IMPORTANT:
These contracts contain NO:
- rollback planning logic
- rollback execution logic
- filesystem mutation logic
- report generation
- business logic

Recovery behavior is implemented by the rollback subsystem.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass
from typing import Optional

from .operations import SkippedOperation
from .validation import (
    validate_list_type,
    validate_non_empty_string,
)


# -------------------------------------------------
# ROLLBACK OPERATION CONTRACT
# -------------------------------------------------
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
    A rollback operation reverses a successful execution:
    - source_path is the current file location
    - destination_path is the original file location
    """

    category: str
    file: str
    source_path: str
    destination_path: str

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


# -------------------------------------------------
# ROLLBACK PLAN CONTRACT
# -------------------------------------------------
@dataclass
class RollbackPlan:
    """
    Represents a deterministic rollback plan generated
    from a persisted execution report.

    CONTRACT GUARANTEES:
    - operations is list[RollbackOperation]
    - skipped is list[SkippedOperation]

    IMPORTANT:
    This contract describes rollback intent only.
    It does NOT indicate rollback success.
    """

    operations: list[RollbackOperation]
    skipped: list[SkippedOperation]

    def __post_init__(self):

        validate_list_type(
            self.operations,
            "operations"
        )

        validate_list_type(
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


# -------------------------------------------------
# ROLLBACK RESULT CONTRACT
# -------------------------------------------------
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