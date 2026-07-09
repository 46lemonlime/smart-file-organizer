# -------------------------------------------------
# ROLLBACK PLANNER
# -------------------------------------------------
"""
Smart File Organizer - Rollback Planner

This module builds deterministic rollback plans from
persisted execution reports.

Responsibilities:
- Read mover execution results from an ExecutionReport
- Identify rollback-eligible operations
- Reverse successful move operations
- Generate skipped rollback diagnostics
- Produce a deterministic RollbackPlan contract

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem discovery
- file filtering
- file classification
- filesystem mutations
- rollback execution
- report persistence
- CLI presentation

Instead, it functions as the rollback planning layer
responsible for transforming persisted execution history
into safe rollback intent.

Rollback Planning Overview:
ExecutionReport
→ mover results inspection
→ rollback operation generation
→ skipped rollback diagnostics
→ RollbackPlan

Input Contract:
Consumes:
- ExecutionReport

Output Contract:
Returns:
- RollbackPlan

Rollback Eligibility:
Only mover results with status="success" are rollback-eligible.

The planner intentionally skips:
- simulated dry-run operations
- failed operations
- skipped operations
- unknown statuses

Design Principles:
- deterministic rollback planning
- no filesystem mutations
- explicit rollback contracts
- safe rollback boundaries
- structured diagnostics
- future-proof recovery foundation
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    ExecutionReport,
    RollbackOperation,
    RollbackPlan,
    SkippedOperation
)


# -------------------------------------------------
# PRIVATE: Build rollback operation
# -------------------------------------------------
def _build_rollback_operation(
    category: str,
    file: str,
    source_path: str,
    destination_path: str
) -> RollbackOperation:
    """
    Builds a rollback operation by reversing a successful
    mover operation.

    IMPORTANT:
    For rollback:
    - source_path is the current moved location
    - destination_path is the original source location
    """

    return RollbackOperation(
        category=category,
        file=file,
        source_path=source_path,
        destination_path=destination_path
    )


# -------------------------------------------------
# PRIVATE: Build skipped rollback operation
# -------------------------------------------------
def _build_skipped_operation(
    reason: str,
    file: str,
    category: str,
    source_path: str
) -> SkippedOperation:
    """
    Builds skipped rollback diagnostics.

    PURPOSE:
    - preserve why a mover result was not rollback-eligible
    - keep rollback planning deterministic
    - expose rollback planning traceability
    """

    return SkippedOperation(
        reason=reason,
        file=file,
        category=category,
        source_path=source_path
    )


# -------------------------------------------------
# PUBLIC: Build rollback plan
# -------------------------------------------------
def build_rollback_plan(
    report: ExecutionReport
) -> RollbackPlan:
    """
    Builds a deterministic rollback plan from an ExecutionReport.

    RETURNS:
        RollbackPlan

    IMPORTANT:
    This function only builds rollback intent.
    It does NOT validate filesystem state and does NOT mutate files.
    Runtime filesystem validation belongs to rollback executor.
    """

    operations: list[RollbackOperation] = []
    skipped: list[SkippedOperation] = []

    for result in report.mover.results:

        # -------------------------------------------------
        # ONLY REAL SUCCESSFUL MOVES CAN BE ROLLED BACK
        # -------------------------------------------------
        if result.status != "success":

            skipped.append(
                _build_skipped_operation(
                    reason=f"rollback_not_allowed_for_{result.status}",
                    file=result.file,
                    category=result.category,
                    source_path=result.destination_path
                )
            )

            continue

        # -------------------------------------------------
        # REVERSE MOVE PATHS
        # -------------------------------------------------
        operations.append(
            _build_rollback_operation(
                category=result.category,
                file=result.file,
                source_path=result.destination_path,
                destination_path=result.source_path
            )
        )

    return RollbackPlan(
        operations=operations,
        skipped=skipped
    )