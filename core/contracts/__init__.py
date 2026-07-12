# -------------------------------------------------
# SMART FILE ORGANIZER - CORE CONTRACTS
# -------------------------------------------------
"""
Public contract exports for Smart File Organizer.

This package exposes the application's shared contracts
through a stable import surface.

Consumers should import contracts directly from:

    core.contracts

rather than individual contract modules whenever possible.
"""

from .configuration import (
    AppConfig,
    CategoryConfig,
)

from .inventory import (
    ClassifiedDiscovery,
    DiscoveryResult,
    DiscoverySkippedItem,
    DiscoveredItem,
    RawDiscoveryDataset,
)

from .operations import (
    ExecutionOperation,
    ExecutionPlan,
    ExecutionResult,
    SkippedOperation,
)

from .recovery import (
    RollbackOperation,
    RollbackPlan,
    RollbackResult,
)

from .records import (
    CategoryReport,
    DiscoveryReport,
    ExecutionReport,
    MoverReport,
    PlanningReport,
    ReportHistoryItem,
    RollbackReport,
)